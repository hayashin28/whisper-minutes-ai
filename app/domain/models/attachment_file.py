from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class AttachmentFile:
    """
    補助資料1件を表すDTO。

    なぜ:
        添付資料を、ただのパス文字列ではなく
        「受理された補助入力」という意味を持つ単位で扱うためです。
        これにより、CurrentWorkContext・Job・AttachmentProcessingService の間で
        同じ粒度の情報を安全に受け渡せます。

    前提:
        このクラスは「添付された事実」と「ファイル属性」のみを持ちます。
        本文読取、文字コード判定、OCR、補助情報抽出は持ちません。

    入出力:
        path, file_name, extension, media_type などを保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    attachment_id: str
    path: str
    file_name: str
    extension: str
    media_type: str  # "text" | "pdf" | "image" | "spreadsheet" | "other"
    size_bytes: int | None
    accepted_at: datetime

    def __post_init__(self) -> None:
        normalized_extension = self.extension.lower()
        normalized_media_type = self.media_type.lower()

        if not self.attachment_id.strip():
            raise ValueError("attachment_id は空にできません。")

        if not self.path.strip():
            raise ValueError("path は空にできません。")

        if not self.file_name.strip():
            raise ValueError("file_name は空にできません。")

        if not normalized_extension.startswith("."):
            raise ValueError("extension は '.txt' のようにドット付きで指定してください。")

        allowed_media_types = {"text", "pdf", "image", "spreadsheet", "other"}
        if normalized_media_type not in allowed_media_types:
            raise ValueError(
                "media_type は 'text', 'pdf', 'image', 'spreadsheet', 'other' のいずれかを指定してください。"
            )

        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes は 0 以上、または None を指定してください。")

        object.__setattr__(self, "extension", normalized_extension)
        object.__setattr__(self, "media_type", normalized_media_type)

    @classmethod
    def from_path(
        cls,
        attachment_id: str,
        path: str,
        size_bytes: int | None = None,
        accepted_at: datetime | None = None,
    ) -> "AttachmentFile":
        """
        パス文字列から AttachmentFile を組み立てる補助コンストラクタです。

        なぜ:
            フロント層ではドラッグ＆ドロップやファイル選択の結果として
            まず path を受け取るため、そこから DTO を安全に作る入口を揃えるためです。
        """
        p = Path(path)
        extension = p.suffix.lower()

        return cls(
            attachment_id=attachment_id,
            path=str(p),
            file_name=p.name,
            extension=extension,
            media_type=_infer_media_type(extension),
            size_bytes=size_bytes,
            accepted_at=accepted_at or datetime.now(),
        )


def _infer_media_type(extension: str) -> str:
    """
    拡張子から添付資料の大分類を推定します。

    なぜ:
        Reader 選択や受理可否判定の前段で、
        粗い媒体分類を持っていると後続の見通しが良くなるためです。
    """
    ext = extension.lower()

    if ext in {".txt", ".md", ".csv"}:
        return "text"

    if ext == ".pdf":
        return "pdf"

    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}:
        return "image"

    if ext in {".xlsx", ".xls"}:
        return "spreadsheet"

    return "other"