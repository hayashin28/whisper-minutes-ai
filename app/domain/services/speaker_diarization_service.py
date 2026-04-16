from __future__ import annotations

from app.domain.models.diarization_result import DiarizationResult
from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings


class SpeakerDiarizationService:
    """
    話者分離サービスの空骨格です。

    なぜ:
        CreateTranscriptJobUseCase から見て、
        話者分離フェーズの責務境界を先に立てるためです。

    前提:
        まだ whisperx などの具体実装は未接続です。
        現段階では、呼び出しても落ちず、
        DiarizationResult を返せることを優先します。

    入出力:
        主入力メディアと設定を受け取り、
        話者分離結果DTOを返します。

    副作用:
        ありません。

    例外:
        基本的に投げません。
        未実装部分は段階的に埋めます。
    """

    def analyze(
        self,
        media_file: MediaFile,
        settings: TranscriptSettings,
    ) -> DiarizationResult:
        """
        話者分離を実行します。

        現段階では空結果を返します。
        ただし、設定で話者分離が無効なら、その旨を warning に残します。
        """
        if not settings.enable_diarization:
            return DiarizationResult(
                warnings=["diarization_disabled"]
            )

        return DiarizationResult.empty()