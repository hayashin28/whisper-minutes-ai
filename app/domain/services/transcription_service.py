from __future__ import annotations

from faster_whisper import WhisperModel

from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings
from app.domain.models.transcription_result import TranscriptSegment, TranscriptionResult


class TranscriptionService:
    """
    faster-whisper を用いた文字起こしサービスです。

    この段階では、UI 起動を妨げないように
    モデルは遅延初期化します。
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._model: WhisperModel | None = None

    def transcribe(
        self,
        media_file: MediaFile,
        settings: TranscriptSettings,
    ) -> TranscriptionResult:
        """
        主入力メディアを文字起こしします。
        """
        model = self._get_model()

        segments, info = model.transcribe(
            media_file.path,
            language=settings.language,
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=True,
        )

        realized_segments = list(segments)

        transcript_segments: list[TranscriptSegment] = []
        full_text_parts: list[str] = []

        for seg in realized_segments:
            text = seg.text.strip()
            if not text:
                continue

            transcript_segments.append(
                TranscriptSegment(
                    start_sec=float(seg.start),
                    end_sec=float(seg.end),
                    text=text,
                    speaker_label=None,
                )
            )
            full_text_parts.append(text)

        full_text = "\n".join(full_text_parts).strip()

        if not full_text:
            return TranscriptionResult.empty(language=settings.language)

        raw_metadata = {
            "detected_language": getattr(info, "language", settings.language),
            "language_probability": str(getattr(info, "language_probability", "")),
        }

        return TranscriptionResult(
            full_text=full_text,
            segments=transcript_segments,
            language=settings.language,
            duration_sec=None,
            raw_metadata=raw_metadata,
            warnings=[],
        )

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )
        return self._model