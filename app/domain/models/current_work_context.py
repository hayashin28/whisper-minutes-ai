from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.attachment_file import AttachmentFile
from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings


@dataclass
class CurrentWorkContext:
    """
    現在画面で扱っている作業コンテキストを表すDTO。

    なぜ:
        実行履歴として残す TranscriptJob と、
        いま画面で触っている状態を分離するためです。
        これにより、主入力差し替え時のリセットや、
        実行前のUI状態管理を安全に扱えます。

    前提:
        このクラスは「今の状態」を保持するだけです。
        文字起こし処理やジョブ実行そのものは持ちません。

    入出力:
        現在の主入力、添付資料、設定、進捗表示用情報、
        プレビュー文字列、アクティブジョブIDを保持します。

    副作用:
        ありません。

    例外:
        基本的に持ちません。
        ただし setter 的な操作は別UseCase側で整合を取る前提です。
    """

    # 現在入力
    current_media_file: MediaFile | None = None
    current_attachments: list[AttachmentFile] = field(default_factory=list)

    # 現在設定
    current_settings: TranscriptSettings = field(default_factory=TranscriptSettings)

    # 現在表示
    preview_text: str = ""
    progress_phase: str = ""
    progress_ratio: float = 0.0
    last_error_message: str | None = None

    # 現在の実行ひも付け
    active_job_id: str | None = None

    def can_execute(self) -> bool:
        """
        現在の状態で実行可能かを返します。

        なぜ:
            実行ボタンの有効/無効や、多重実行防止の前段判定に使いやすくするためです。

        判定方針:
            - 主入力が存在すること
            - 実行中ジョブがぶら下がっていないこと
        """
        return self.current_media_file is not None and self.active_job_id is None

    def reset_for_media_replacement(self) -> None:
        """
        主入力差し替え時の現在状態リセットを行います。

        なぜ:
            基本設計で、対象メディア差し替え時は
            現在状態をリセットする方針が固定されているためです。

        注意:
            これは「現在状態」だけを初期化します。
            ジョブ履歴は別責務なので触りません。
        """
        self.current_media_file = None
        self.current_attachments.clear()
        self.current_settings = TranscriptSettings()
        self.preview_text = ""
        self.progress_phase = ""
        self.progress_ratio = 0.0
        self.last_error_message = None
        self.active_job_id = None

    def clear_runtime_state(self) -> None:
        """
        実行時にぶら下がる表示系状態だけを初期化します。

        なぜ:
            主入力や添付資料は残したまま、
            実行結果や進捗表示だけを消したい場面があるためです。
        """
        self.preview_text = ""
        self.progress_phase = ""
        self.progress_ratio = 0.0
        self.last_error_message = None
        self.active_job_id = None