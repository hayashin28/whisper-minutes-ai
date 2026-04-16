from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AttachmentReadResult:
    """
    添付資料1件の読込結果を表すDTO。

    なぜ:
        「添付されたこと」と「読めたこと」は別だからです。
        受理済みだが未読取、読取成功、読取失敗を
        明示的に分けて扱えるようにします。

    前提:
        このクラスは結果保持のみを担当します。
        実際の読込や文字コード判定は Reader / Service 側の責務です。

    入出力:
        添付資料ID、受理可否、読取成功可否、抽出本文、
        文字コード、警告、エラーを保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    attachment_id: str
    file_name: str
    file_type: str

    accepted: bool
    read_success: bool

    decoded_charset: str | None = None
    extracted_text: str | None = None
    raw_metadata: dict[str, str] | None = None

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized_attachment_id = self.attachment_id.strip()
        normalized_file_name = self.file_name.strip()
        normalized_file_type = self.file_type.strip().lower()
        normalized_decoded_charset = self.decoded_charset.strip().lower() if self.decoded_charset else None

        if not normalized_attachment_id:
            raise ValueError("attachment_id は空にできません。")

        if not normalized_file_name:
            raise ValueError("file_name は空にできません。")

        if not normalized_file_type:
            raise ValueError("file_type は空にできません。")

        if self.read_success and self.extracted_text is None:
            raise ValueError("read_success=True の場合、extracted_text は None にできません。")

        object.__setattr__(self, "attachment_id", normalized_attachment_id)
        object.__setattr__(self, "file_name", normalized_file_name)
        object.__setattr__(self, "file_type", normalized_file_type)
        object.__setattr__(self, "decoded_charset", normalized_decoded_charset)

    @classmethod
    def accepted_but_not_read(
        cls,
        attachment_id: str,
        file_name: str,
        file_type: str,
        warning: str = "accepted_but_not_used",
    ) -> "AttachmentReadResult":
        """
        受理はしたが、まだ本文読取していない状態を表す補助コンストラクタです。
        """
        return cls(
            attachment_id=attachment_id,
            file_name=file_name,
            file_type=file_type,
            accepted=True,
            read_success=False,
            warnings=[warning],
        )

    @classmethod
    def read_successfully(
        cls,
        attachment_id: str,
        file_name: str,
        file_type: str,
        extracted_text: str,
        decoded_charset: str | None = None,
        raw_metadata: dict[str, str] | None = None,
        warnings: list[str] | None = None,
    ) -> "AttachmentReadResult":
        """
        読取成功状態を表す補助コンストラクタです。
        """
        return cls(
            attachment_id=attachment_id,
            file_name=file_name,
            file_type=file_type,
            accepted=True,
            read_success=True,
            decoded_charset=decoded_charset,
            extracted_text=extracted_text,
            raw_metadata=raw_metadata,
            warnings=list(warnings or []),
        )

    @classmethod
    def failed_to_read(
        cls,
        attachment_id: str,
        file_name: str,
        file_type: str,
        error: str,
    ) -> "AttachmentReadResult":
        """
        読取失敗状態を表す補助コンストラクタです。
        """
        return cls(
            attachment_id=attachment_id,
            file_name=file_name,
            file_type=file_type,
            accepted=True,
            read_success=False,
            errors=[error],
        )