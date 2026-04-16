from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class MediaFile:
    """
    主入力である音声または動画ファイル1件を表すDTO。

    なぜ:
        文字起こし対象ファイルを、ただの文字列パスではなく
        意味を持つオブジェクトとして扱うためです。
        これにより、UseCase・Job・UI のあいだで
        「何が主入力か」をぶれずに受け渡せます。

    前提:
        このクラスは入力として確定したファイル情報だけを持ちます。
        音声長取得、実在確認、文字起こし処理そのものは持ちません。

    入出力:
        path, file_name, extension, media_kind などを保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    media_id: str
    path: str
    file_name: str
    extension: str
    media_kind: str  # "audio" or "video"
    size_bytes: int | None
    selected_at: datetime

    def __post_init__(self) -> None:
        normalized_extension = self.extension.lower()
        normalized_media_kind = self.media_kind.lower()

        if not self.media_id.strip():
            raise ValueError("media_id は空にできません。")

        if not self.path.strip():
            raise ValueError("path は空にできません。")

        if not self.file_name.strip():
            raise ValueError("file_name は空にできません。")

        if not normalized_extension.startswith("."):
            raise ValueError("extension は '.mp3' のようにドット付きで指定してください。")

        if normalized_media_kind not in {"audio", "video"}:
            raise ValueError("media_kind は 'audio' または 'video' を指定してください。")

        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes は 0 以上、または None を指定してください。")

        object.__setattr__(self, "extension", normalized_extension)
        object.__setattr__(self, "media_kind", normalized_media_kind)

    @classmethod
    def from_path(
        cls,
        media_id: str,
        path: str,
        media_kind: str,
        size_bytes: int | None = None,
        selected_at: datetime | None = None,
    ) -> "MediaFile":
        """
        パス文字列から MediaFile を組み立てる補助コンストラクタです。

        なぜ:
            UI 側ではファイル選択結果として path をまず受け取るため、
            そこから安全に DTO を作る入口を用意しておくと配線が楽になります。
        """
        p = Path(path)
        return cls(
            media_id=media_id,
            path=str(p),
            file_name=p.name,
            extension=p.suffix.lower(),
            media_kind=media_kind,
            size_bytes=size_bytes,
            selected_at=selected_at or datetime.now(),
        )