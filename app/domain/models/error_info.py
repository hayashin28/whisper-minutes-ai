from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorInfo:
    """
    ジョブ全体、または主要処理単位における継続不能エラーを表すDTO。

    なぜ:
        例外文字列をそのままUIや履歴へ流さず、
        保存・表示・判定に使える形へ整えるためです。

    前提:
        このクラスは「失敗情報」を保持するだけです。
        失敗判定そのものは UseCase 側の責務です。

    入出力:
        エラーコード、表示用メッセージ、詳細、失敗フェーズ、
        例外型名を保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    code: str
    message: str
    detail: str | None = None
    failed_phase: str | None = None
    exception_type: str | None = None

    def __post_init__(self) -> None:
        normalized_code = self.code.strip().upper()
        normalized_message = self.message.strip()
        normalized_failed_phase = self.failed_phase.strip().upper() if self.failed_phase else None
        normalized_exception_type = self.exception_type.strip() if self.exception_type else None

        if not normalized_code:
            raise ValueError("code は空にできません。")

        if not normalized_message:
            raise ValueError("message は空にできません。")

        object.__setattr__(self, "code", normalized_code)
        object.__setattr__(self, "message", normalized_message)
        object.__setattr__(self, "failed_phase", normalized_failed_phase)
        object.__setattr__(self, "exception_type", normalized_exception_type)

    @classmethod
    def from_exception(
        cls,
        code: str,
        message: str,
        exc: Exception,
        failed_phase: str | None = None,
    ) -> "ErrorInfo":
        """
        例外オブジェクトから ErrorInfo を組み立てる補助コンストラクタです。

        なぜ:
            UseCase 側で except した例外を、そのまま保存・返却できる形へ
            揃える入口があると実装が散らばりにくいためです。
        """
        return cls(
            code=code,
            message=message,
            detail=str(exc),
            failed_phase=failed_phase,
            exception_type=type(exc).__name__,
        )