from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.progress_reporter import ProgressReporter
from app.domain.models.attachment_file import AttachmentFile
from app.domain.models.error_info import ErrorInfo
from app.domain.models.formatted_transcript import FormattedTranscript
from app.domain.models.job_status import JobStatus
from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_job import TranscriptJob
from app.domain.models.transcript_settings import TranscriptSettings
from app.domain.services.attachment_processing_service import AttachmentProcessingService
from app.domain.services.speaker_diarization_service import SpeakerDiarizationService
from app.domain.services.transcription_service import TranscriptionService
from app.domain.services.transcript_formatting_service import TranscriptFormattingService


@dataclass(frozen=True)
class CreateTranscriptJobInput:
    media_file: MediaFile
    attachments: list[AttachmentFile]
    settings: TranscriptSettings


@dataclass(frozen=True)
class CreateTranscriptJobOutput:
    job_id: str
    status: JobStatus
    formatted_transcript: FormattedTranscript | None = None
    error_info: ErrorInfo | None = None


class CreateTranscriptJobUseCase:
    def __init__(
        self,
        job_repository: JobRepository,
        progress_reporter: ProgressReporter,
        attachment_processing_service: AttachmentProcessingService,
        speaker_diarization_service: SpeakerDiarizationService,
        transcription_service: TranscriptionService,
        transcript_formatting_service: TranscriptFormattingService,
    ) -> None:
        self._job_repository = job_repository
        self._progress_reporter = progress_reporter
        self._attachment_processing_service = attachment_processing_service
        self._speaker_diarization_service = speaker_diarization_service
        self._transcription_service = transcription_service
        self._transcript_formatting_service = transcript_formatting_service

    def execute(self, input_data: CreateTranscriptJobInput) -> CreateTranscriptJobOutput:
        job = TranscriptJob(
            job_id=self._generate_job_id(),
            started_at=datetime.now(),
            media_file=input_data.media_file,
            attachments=list(input_data.attachments),
            settings=input_data.settings,
            status=JobStatus.READY,
            progress_phase="準備中",
            progress_ratio=0.0,
        )

        self._save_and_report(job)

        try:
            job.mark_progress(
                status=JobStatus.ATTACHMENT_PROCESSING,
                phase="添付資料処理中",
                ratio=0.1,
            )
            self._save_and_report(job)

            attachment_read_results, attachment_supplement = (
                self._attachment_processing_service.process(job.attachments)
            )
            job.attachment_read_results = attachment_read_results
            job.attachment_supplement = attachment_supplement
            self._save_and_report(job)

            job.mark_progress(
                status=JobStatus.DIARIZING,
                phase="話者分離中",
                ratio=0.3,
            )
            self._save_and_report(job)

            diarization_result = self._speaker_diarization_service.analyze(
                media_file=job.media_file,
                settings=job.settings,
            )
            job.diarization_result = diarization_result
            self._save_and_report(job)

            job.mark_progress(
                status=JobStatus.TRANSCRIBING,
                phase="文字起こし中",
                ratio=0.6,
            )
            self._save_and_report(job)

            transcription_result = self._transcription_service.transcribe(
                media_file=job.media_file,
                settings=job.settings,
            )
            job.transcription_result = transcription_result
            self._save_and_report(job)

            job.mark_progress(
                status=JobStatus.FORMATTING,
                phase="整形中",
                ratio=0.8,
            )
            self._save_and_report(job)

            formatted_transcript = self._transcript_formatting_service.format(
                transcription_result=job.transcription_result,
                diarization_result=job.diarization_result,
                attachment_supplement=job.attachment_supplement,
                settings=job.settings,
                source_job_id=job.job_id,
            )
            job.formatted_transcript = formatted_transcript
            self._save_and_report(job)

            job.mark_completed(
                formatted_transcript=formatted_transcript,
                finished_at=datetime.now(),
            )
            self._save_and_report(job)

            return CreateTranscriptJobOutput(
                job_id=job.job_id,
                status=job.status,
                formatted_transcript=formatted_transcript,
                error_info=None,
            )

        except Exception as exc:
            error_info = ErrorInfo.from_exception(
                code="JOB_EXECUTION_FAILED",
                message="ジョブ実行中に失敗しました。",
                exc=exc,
                failed_phase=job.status.value,
            )
            job.mark_failed(error_info=error_info, finished_at=datetime.now())
            self._save_and_report(job)

            return CreateTranscriptJobOutput(
                job_id=job.job_id,
                status=job.status,
                formatted_transcript=None,
                error_info=error_info,
            )

    def _save_and_report(self, job: TranscriptJob) -> None:
        self._job_repository.save(job)
        self._progress_reporter.report(job.progress_phase, job.progress_ratio)

    def _generate_job_id(self) -> str:
        return uuid4().hex