from __future__ import annotations

from app.application.create_transcript_job_usecase import (
    CreateTranscriptJobInput,
    CreateTranscriptJobUseCase,
)
from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings
from app.domain.services.attachment_processing_service import AttachmentProcessingService
from app.domain.services.speaker_diarization_service import SpeakerDiarizationService
from app.domain.services.transcription_service import TranscriptionService
from app.infrastructure.reporters.null_progress_reporter import NullProgressReporter
from app.infrastructure.repositories.in_memory_job_repository import InMemoryJobRepository


def main() -> None:
    job_repository = InMemoryJobRepository()
    progress_reporter = NullProgressReporter()
    attachment_processing_service = AttachmentProcessingService()
    speaker_diarization_service = SpeakerDiarizationService()
    transcription_service = TranscriptionService()

    create_transcript_job_usecase = CreateTranscriptJobUseCase(
        job_repository=job_repository,
        progress_reporter=progress_reporter,
        attachment_processing_service=attachment_processing_service,
        speaker_diarization_service=speaker_diarization_service,
        transcription_service=transcription_service,
    )

    media_file = MediaFile.from_path(
        media_id="media-001",
        path=r"D:\workspace\sample.mp3",
        media_kind="audio",
    )

    settings = TranscriptSettings()

    input_data = CreateTranscriptJobInput(
        media_file=media_file,
        attachments=[],
        settings=settings,
    )

    output_data = create_transcript_job_usecase.execute(input_data)
    saved_job = job_repository.find_by_id(output_data.job_id)

    print("=== 実行結果 ===")
    print(f"job_id: {output_data.job_id}")
    print(f"status: {output_data.status}")
    print("--- 保存確認 ---")
    print(saved_job)


if __name__ == "__main__":
    main()