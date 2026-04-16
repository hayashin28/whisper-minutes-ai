from __future__ import annotations

from app.domain.models.diarization_result import DiarizationResult
from app.domain.models.formatted_transcript import FormattedTranscript
from app.domain.models.transcript_settings import TranscriptSettings
from app.domain.models.transcription_result import TranscriptionResult
from app.domain.services.attachment_processing_service import AttachmentSupplement


class TranscriptFormattingService:
    """
    整形サービスの空骨格です。

    なぜ:
        生の文字起こし結果と、最終的に表示する整形済み結果を
        分離するためです。

    前提:
        現段階では最小のダミー整形に留めます。
        話者A/B/C の本格整形や添付資料を使った補強は、後で段階的に足します。

    入出力:
        文字起こし結果、話者分離結果、添付補助情報、設定を受け取り、
        FormattedTranscript を返します。

    副作用:
        ありません。

    例外:
        基本的に投げません。
    """

    def format(
        self,
        transcription_result: TranscriptionResult,
        diarization_result: DiarizationResult | None,
        attachment_supplement: AttachmentSupplement | None,
        settings: TranscriptSettings,
        source_job_id: str | None = None,
    ) -> FormattedTranscript:
        """
        最終表示用の整形済み文字起こし結果を返します。

        現段階では、単一話者前提の最小整形のみ行います。
        """
        text = (
            "【話者情報】\n"
            "単一話者として処理しました。\n\n"
            "【文字起こし】\n"
            f"{transcription_result.full_text}"
        )

        return FormattedTranscript.single_speaker(
            text=text,
            source_job_id=source_job_id,
            warnings=["dummy_formatting_result"],
        )