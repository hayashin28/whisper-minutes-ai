from __future__ import annotations


class NullProgressReporter:
    """
    何もしない ProgressReporter 実装です。

    なぜ:
        UI 未接続の段階でも UseCase を動かせるようにするためです。
        テストや最小動作確認で、進捗通知先を仮置きできます。

    前提:
        この実装は進捗を保持も表示もしません。
        「report が呼ばれても落ちない」ことだけを担保します。

    入出力:
        progress_phase と progress_ratio を受け取りますが、何も返しません。

    副作用:
        ありません。

    例外:
        基本的にありません。
    """

    def report(self, progress_phase: str, progress_ratio: float) -> None:
        """
        進捗通知を受け取りますが、何もしません。
        """
        return