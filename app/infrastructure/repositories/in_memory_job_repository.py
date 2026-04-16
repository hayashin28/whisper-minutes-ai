from __future__ import annotations

from app.domain.models.transcript_job import TranscriptJob


class InMemoryJobRepository:
    """
    TranscriptJob をメモリ上で保持する Repository 実装です。

    なぜ:
        MVP の初期段階では、永続化よりも
        UseCase と Job の流れを成立させることが優先だからです。
        この実装を置くことで、JobRepository 境界を保ったまま
        実際に保存・参照の動作確認ができます。

    前提:
        プロセス終了で内容は消えます。
        永続保存は後続段階で別実装へ差し替える想定です。

    入出力:
        save, find_by_id, list_all を提供します。

    副作用:
        インスタンス内部の辞書にジョブを保存します。

    例外:
        特別な例外は投げません。
        存在しない job_id は None を返します。
    """

    def __init__(self) -> None:
        self._jobs: dict[str, TranscriptJob] = {}

    def save(self, job: TranscriptJob) -> None:
        """
        ジョブを保存します。

        同じ job_id がすでに存在する場合は、
        最新の内容で上書きします。
        """
        self._jobs[job.job_id] = job

    def find_by_id(self, job_id: str) -> TranscriptJob | None:
        """
        job_id に対応するジョブを返します。
        存在しない場合は None を返します。
        """
        return self._jobs.get(job_id)

    def list_all(self) -> list[TranscriptJob]:
        """
        保存済みの全ジョブを返します。

        いまは単純に保存順で返します。
        Python 3.7+ の dict は挿入順を保持するため、
        MVP ではこれで十分です。
        """
        return list(self._jobs.values())