from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.attachment_file import AttachmentFile
from app.domain.models.attachment_read_result import AttachmentReadResult


@dataclass(frozen=True)
class AttachmentSupplement:
    """
    添付資料から抽出した、後続処理向け補助情報を表すDTO。

    なぜ:
        添付資料の読込結果そのものと、
        後続の整形や将来のAI補強で参照する補助情報を分けるためです。

    前提:
        MVP 初期段階では最小の器として置きます。
        まだ実際の抽出ロジックは入れません。

    入出力:
        キーワード候補、固有名詞候補、参照文などの席を持ちます。

    副作用:
        ありません。

    例外:
        ありません。
    """

    keywords: list[str] = field(default_factory=list)
    proper_noun_candidates: list[str] = field(default_factory=list)
    reference_sentences: list[str] = field(default_factory=list)
    source_attachment_ids: list[str] = field(default_factory=list)


class AttachmentProcessingService:
    """
    添付資料処理の空骨格サービスです。

    なぜ:
        CreateTranscriptJobUseCase から見て、
        添付資料処理フェーズの責務境界を先に立てるためです。

    前提:
        まだ Reader 群や文字コード処理本体は未接続です。
        現段階では、添付0件でも安定して結果を返せることを優先します。

    入出力:
        添付資料一覧を受け取り、
        読込結果一覧と補助情報を返します。

    副作用:
        ありません。

    例外:
        基本的に投げません。
        未実装部分は段階的に埋めます。
    """

    def process(
        self,
        attachments: list[AttachmentFile],
    ) -> tuple[list[AttachmentReadResult], AttachmentSupplement | None]:
        """
        添付資料一覧を処理します。

        現段階では、
        - 添付0件なら空結果を返す
        - 添付ありでも、まだ本文読取はしない
        という最小骨格です。
        """
        if not attachments:
            return [], None

        read_results = [
            AttachmentReadResult.accepted_but_not_read(
                attachment_id=attachment.attachment_id,
                file_name=attachment.file_name,
                file_type=attachment.extension,
            )
            for attachment in attachments
        ]

        supplement = AttachmentSupplement(
            source_attachment_ids=[attachment.attachment_id for attachment in attachments]
        )

        return read_results, supplement