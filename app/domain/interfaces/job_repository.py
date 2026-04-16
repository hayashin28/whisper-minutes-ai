from __future__ import annotations

from typing import Protocol

from app.domain.models.transcript_job import TranscriptJob


class JobRepository(Protocol):
    """
    TranscriptJob の保存・参照を行うための境界インターフェース。

    なぜ:
        UseCase が保存先の具体実装に依存しないようにするためです。
        MVP ではメモリ実装でも、後で JSON / SQLite / その他へ
        差し替えやすくなります。

    前提:
        この Protocol は保存契約だけを定義します。
        保存形式や永続化手段は concrete 実装側の責務です。

    入出力:
        save, find_by_id, list_all を提供します。

    副作用:
        実装側では保存操作の副作用を持ちますが、
        この Protocol 自体は契約定義のみです。

    例外:
        ここでは定めません。
        実装側で必要に応じて扱います。
    """

    def save(self, job: TranscriptJob) -> None:
        """
        ジョブを保存します。

        同一 job_id がすでに存在する場合は、
        上書き更新する実装を基本方針とします。
        """
        ...

    def find_by_id(self, job_id: str) -> TranscriptJob | None:
        """
        job_id でジョブを1件取得します。
        存在しない場合は None を返します。
        """
        ...

    def list_all(self) -> list[TranscriptJob]:
        """
        保存済みの全ジョブを返します。
        戻り順は実装依存ですが、MVP では保存順または開始時刻順を想定します。
        """
        ...