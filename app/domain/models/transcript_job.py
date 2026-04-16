from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.models.attachment_file import AttachmentFile
from app.domain.models.error_info import ErrorInfo
from app.domain.models.job_status import JobStatus
from app.domain.models.media_file import MediaFile
from app.domain.models.transcript_settings import TranscriptSettings


@dataclass
class TranscriptJob:
    """
    1回の文字起こし実行を表す履歴側DTO。

    なぜ:
        実行時の入力、進行状態、中間結果、最終結果、失敗情報を
        1単位として保持するためです。
        CurrentWorkContext と分けることで、
        「今の画面状態」と「過去の実行履歴」を混同しないようにします。

    前提:
        このクラスは状態保持の器です。
        自身で文字起こし処理や状態遷移判断は行いません。
        状態更新の主体は UseCase 側です。

    入出力:
        主入力、添付資料、設定、ジョブ状態、進捗表示用情報、
        中間結果、最終結果、失敗情報を保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    # 識別・時刻
    job_id: str
    started_at: datetime

    # 入力確定情報
    media_file: MediaFile
    attachments: list[AttachmentFile]
    settings: TranscriptSettings

    # 実行状態
    status: JobStatus = JobStatus.READY
    progress_phase: str = ""
    progress_ratio: float = 0.0

    # 中間結果
    attachment_read_results: list[Any] = field(default_factory=list)
    attachment_supplement: Any | None = None
    diarization_result: Any | None = None
    transcription_result: Any | None = None

    # 最終結果
    formatted_transcript: Any | None = None

    # 失敗情報
    error_info: ErrorInfo | None = None

    # 終了時刻
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_job_id = self.job_id.strip()
        normalized_progress_phase = self.progress_phase.strip()

        if not normalized_job_id:
            raise ValueError("job_id は空にできません。")

        if not 0.0 <= self.progress_ratio <= 1.0:
            raise ValueError("progress_ratio は 0.0 以上 1.0 以下で指定してください。")

        object.__setattr__(self, "job_id", normalized_job_id)
        object.__setattr__(self, "progress_phase", normalized_progress_phase)

    def mark_progress(self, status: JobStatus, phase: str, ratio: float) -> None:
        """
        進捗表示用の状態を更新します。

        なぜ:
            UseCase からの更新操作を読みやすくし、
            status / phase / ratio の更新を1か所に寄せるためです。

        注意:
            状態遷移の正しさそのものは、このメソッドでは検証しません。
            遷移ルールは UseCase 側の責務です。
        """
        if not 0.0 <= ratio <= 1.0:
            raise ValueError("ratio は 0.0 以上 1.0 以下で指定してください。")

        self.status = status
        self.progress_phase = phase.strip()
        self.progress_ratio = ratio

    def mark_completed(self, formatted_transcript: Any, finished_at: datetime | None = None) -> None:
        """
        ジョブを完了状態にします。
        """
        self.status = JobStatus.COMPLETED
        self.progress_phase = "完了"
        self.progress_ratio = 1.0
        self.formatted_transcript = formatted_transcript
        self.finished_at = finished_at or datetime.now()
        self.error_info = None

    def mark_failed(self, error_info: ErrorInfo, finished_at: datetime | None = None) -> None:
        """
        ジョブを失敗状態にします。
        """
        self.status = JobStatus.FAILED
        self.progress_phase = "失敗"
        self.finished_at = finished_at or datetime.now()
        self.error_info = error_info