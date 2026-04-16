from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FormattedTranscript:
    """
    整形済み文字起こし結果を表すDTO。

    なぜ:
        生の文字起こし結果と、最終的に表示・出力する結果を
        分離するためです。
        これにより、文字起こし責務と整形責務を混同しないようにします。

    前提:
        このクラスは完成済みテキストを保持するだけです。
        整形ロジックそのものは TranscriptFormattingService 側の責務です。

    入出力:
        表示用本文、話者モード、使用した話者ラベル、
        元ジョブID、警告を保持します。

    副作用:
        ありません。

    例外:
        __post_init__ で最低限の不正値を弾きます。
    """

    text: str
    speaker_mode: str  # "single" | "multi"
    speaker_labels_used: list[str] = field(default_factory=list)
    source_job_id: str | None = None
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized_text = self.text.strip()
        normalized_speaker_mode = self.speaker_mode.strip().lower()
        normalized_speaker_labels = [label.strip().upper() for label in self.speaker_labels_used]
        normalized_source_job_id = self.source_job_id.strip() if self.source_job_id else None

        if not normalized_text:
            raise ValueError("text は空にできません。")

        allowed_speaker_modes = {"single", "multi"}
        if normalized_speaker_mode not in allowed_speaker_modes:
            raise ValueError("speaker_mode は 'single' または 'multi' を指定してください。")

        if any(not label for label in normalized_speaker_labels):
            raise ValueError("speaker_labels_used に空文字は指定できません。")

        object.__setattr__(self, "text", normalized_text)
        object.__setattr__(self, "speaker_mode", normalized_speaker_mode)
        object.__setattr__(self, "speaker_labels_used", normalized_speaker_labels)
        object.__setattr__(self, "source_job_id", normalized_source_job_id)

    @classmethod
    def single_speaker(
        cls,
        text: str,
        source_job_id: str | None = None,
        warnings: list[str] | None = None,
    ) -> "FormattedTranscript":
        """
        単一話者用の整形済み結果を作る補助コンストラクタです。
        """
        return cls(
            text=text,
            speaker_mode="single",
            speaker_labels_used=["A"],
            source_job_id=source_job_id,
            warnings=list(warnings or []),
        )

    @classmethod
    def multi_speaker(
        cls,
        text: str,
        speaker_labels_used: list[str],
        source_job_id: str | None = None,
        warnings: list[str] | None = None,
    ) -> "FormattedTranscript":
        """
        複数話者用の整形済み結果を作る補助コンストラクタです。
        """
        return cls(
            text=text,
            speaker_mode="multi",
            speaker_labels_used=speaker_labels_used,
            source_job_id=source_job_id,
            warnings=list(warnings or []),
        )