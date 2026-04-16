from __future__ import annotations

from typing import Protocol


class ProgressReporter(Protocol):
    """
    ジョブ進捗を通知するための境界インターフェース。

    なぜ:
        UseCase が GUI 実装に直接依存しないようにするためです。
        これにより、Tkinter / CustomTkinter / テスト用ダミー実装を
        差し替えやすくなります。

    前提:
        この Protocol は「進捗通知の契約」だけを定義します。
        画面描画、スレッド切り替え、ラベル更新などの具体処理は
        実装側の責務です。

    入出力:
        progress_phase と progress_ratio を受け取ります。

    副作用:
        実装側では UI 更新などの副作用を持ちますが、
        この Protocol 自体は契約定義のみです。

    例外:
        ここでは定めません。
        実装側で必要に応じて扱います。
    """

    def report(self, progress_phase: str, progress_ratio: float) -> None:
        """
        進捗を通知します。

        Parameters
        ----------
        progress_phase:
            現在どの工程かを表す文言です。
            例: "添付資料処理中", "話者分離中", "文字起こし中"

        progress_ratio:
            0.0 ～ 1.0 の進捗率です。
        """
        ...