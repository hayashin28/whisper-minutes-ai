from __future__ import annotations

from app.application.create_transcript_job_usecase import CreateTranscriptJobUseCase
from app.domain.services.attachment_processing_service import AttachmentProcessingService
from app.domain.services.speaker_diarization_service import SpeakerDiarizationService
from app.domain.services.transcription_service import TranscriptionService
from app.domain.services.transcript_formatting_service import TranscriptFormattingService
from app.front.whisper_app_window import WhisperAppWindow
from app.infrastructure.reporters.callback_progress_reporter import CallbackProgressReporter
from app.infrastructure.repositories.in_memory_job_repository import InMemoryJobRepository


def main() -> None:
    app = WhisperAppWindow()

    job_repository = InMemoryJobRepository()
    progress_reporter = CallbackProgressReporter(app.handle_progress_update)
    attachment_processing_service = AttachmentProcessingService()
    speaker_diarization_service = SpeakerDiarizationService()
    transcription_service = TranscriptionService()
    transcript_formatting_service = TranscriptFormattingService()

    create_transcript_job_usecase = CreateTranscriptJobUseCase(
        job_repository=job_repository,
        progress_reporter=progress_reporter,
        attachment_processing_service=attachment_processing_service,
        speaker_diarization_service=speaker_diarization_service,
        transcription_service=transcription_service,
        transcript_formatting_service=transcript_formatting_service,
    )

    app.set_create_transcript_job_usecase(create_transcript_job_usecase)
    app.mainloop()


if __name__ == "__main__":
    main()