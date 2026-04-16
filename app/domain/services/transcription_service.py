from __future__ import annotations

from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings
from app.domain.models.transcription_result import TranscriptionResult


class TranscriptionService:
    """
    文字起こしサービスの空骨格です。

    なぜ:
        CreateTranscriptJobUseCase から見て、
        TRANSCRIBING フェーズの責務境界を先に立てるためです。

    前提:
        まだ faster-whisper などの具体実装は未接続です。
        現段階では、呼び出しても落ちず、
        TranscriptionResult を返せることを優先します。

    入出力:
        主入力メディアと設定を受け取り、
        生の文字起こし結果DTOを返します。

    副作用:
        ありません。

    例外:
        基本的に投げません。
        未実装部分は段階的に埋めます。
    """

    def transcribe(
        self,
        media_file: MediaFile,
        settings: TranscriptSettings,
    ) -> TranscriptionResult:
        """
        文字起こしを実行します。

        現段階ではダミー結果を返します。
        後で faster-whisper 等へ差し替える前提です。
        """
        dummy_text = f"[DUMMY] {media_file.file_name} の文字起こし結果です。"

        return TranscriptionResult.from_text(
            full_text=dummy_text,
            language=settings.language,
            duration_sec=None,
            warnings=["dummy_transcription_result"],
        )