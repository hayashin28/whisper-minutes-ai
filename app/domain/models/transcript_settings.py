from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptSettings:
    """
    文字起こし実行時の設定を表すDTO。

    なぜ:
        実行条件を個別引数として散らさず、
        1つの設定オブジェクトとして扱うためです。
        これにより、CurrentWorkContext・UseCase・TranscriptJob の間で
        同じ条件をぶれずに受け渡せます。

    前提:
        このクラスは「設定値」を持つだけです。
        UI 部品の状態や、実際の処理ロジックは持ちません。

    入出力:
        言語、話者分離の有無、添付資料利用、出力方針などを保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で不正値を最低限弾きます。
    """

    # 基本設定
    language: str = "ja"
    enable_diarization: bool = True
    use_attachments: bool = True

    # 出力設定
    output_mode: str = "formatted_text"
    single_speaker_policy: str = "header_only"
    multi_speaker_label_style: str = "alphabetic"

    # 将来拡張席
    enable_ai_enhancement: bool = False
    enable_ocr: bool = False
    attachment_scope: str = "minimal"

    def __post_init__(self) -> None:
        normalized_language = self.language.strip().lower()
        normalized_output_mode = self.output_mode.strip().lower()
        normalized_single_speaker_policy = self.single_speaker_policy.strip().lower()
        normalized_multi_speaker_label_style = self.multi_speaker_label_style.strip().lower()
        normalized_attachment_scope = self.attachment_scope.strip().lower()

        if not normalized_language:
            raise ValueError("language は空にできません。")

        allowed_output_modes = {"formatted_text"}
        if normalized_output_mode not in allowed_output_modes:
            raise ValueError(
                "output_mode は現在 'formatted_text' のみ対応です。"
            )

        allowed_single_speaker_policies = {"header_only"}
        if normalized_single_speaker_policy not in allowed_single_speaker_policies:
            raise ValueError(
                "single_speaker_policy は現在 'header_only' のみ対応です。"
            )

        allowed_multi_speaker_label_styles = {"alphabetic"}
        if normalized_multi_speaker_label_style not in allowed_multi_speaker_label_styles:
            raise ValueError(
                "multi_speaker_label_style は現在 'alphabetic' のみ対応です。"
            )

        allowed_attachment_scopes = {"minimal", "full"}
        if normalized_attachment_scope not in allowed_attachment_scopes:
            raise ValueError(
                "attachment_scope は 'minimal' または 'full' を指定してください。"
            )

        object.__setattr__(self, "language", normalized_language)
        object.__setattr__(self, "output_mode", normalized_output_mode)
        object.__setattr__(self, "single_speaker_policy", normalized_single_speaker_policy)
        object.__setattr__(self, "multi_speaker_label_style", normalized_multi_speaker_label_style)
        object.__setattr__(self, "attachment_scope", normalized_attachment_scope)