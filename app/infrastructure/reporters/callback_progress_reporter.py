from __future__ import annotations

from collections.abc import Callable


class CallbackProgressReporter:
    """
    進捗通知をコールバック関数へ橋渡しする ProgressReporter 実装です。

    なぜ:
        UseCase が GUI 実装に依存せず、
        UI 側は必要な表示更新だけを受け取れるようにするためです。

    前提:
        この段階では同期実行を前提とします。
        後でスレッド化する場合も、この境界はそのまま活かせます。
    """

    def __init__(self, callback: Callable[[str, float], None]) -> None:
        self._callback = callback

    def report(self, progress_phase: str, progress_ratio: float) -> None:
        self._callback(progress_phase, progress_ratio)