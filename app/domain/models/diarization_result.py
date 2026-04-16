from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SpeakerSegment:
    """
    話者分離における1区間を表すDTO。

    なぜ:
        話者分離結果を、開始秒・終了秒・話者ラベルの単位で
        後続処理へ渡せるようにするためです。

    前提:
        人物名は持ちません。
        あくまで A/B/C のような抽象ラベルだけを扱います。
    """

    start_sec: float
    end_sec: float
    speaker_label: str

    def __post_init__(self) -> None:
        normalized_label = self.speaker_label.strip().upper()

        if self.start_sec < 0:
            raise ValueError("start_sec は 0 以上で指定してください。")

        if self.end_sec < 0:
            raise ValueError("end_sec は 0 以上で指定してください。")

        if self.end_sec < self.start_sec:
            raise ValueError("end_sec は start_sec 以上で指定してください。")

        if not normalized_label:
            raise ValueError("speaker_label は空にできません。")

        object.__setattr__(self, "speaker_label", normalized_label)


@dataclass(frozen=True)
class DiarizationResult:
    """
    話者分離結果を表すDTO。

    なぜ:
        単一話者 / 複数話者の分岐や、
        後続の整形処理に必要な最小情報をまとめるためです。

    前提:
        人物名推論は行いません。
        ラベルは A/B/C のような抽象表現に留めます。
    """

    segments: list[SpeakerSegment] = field(default_factory=list)
    speaker_count: int = 0
    is_single_speaker: bool = True
    speaker_labels: list[str] = field(default_factory=list)
    raw_metadata: dict[str, str] | None = None
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized_labels = [label.strip().upper() for label in self.speaker_labels]

        if self.speaker_count < 0:
            raise ValueError("speaker_count は 0 以上で指定してください。")

        if any(not label for label in normalized_labels):
            raise ValueError("speaker_labels に空文字は指定できません。")

        object.__setattr__(self, "speaker_labels", normalized_labels)

    @classmethod
    def empty(cls) -> "DiarizationResult":
        """
        まだ有効な話者分離結果が無い状態を表す補助コンストラクタです。
        """
        return cls()

    @classmethod
    def single_speaker(
        cls,
        segments: list[SpeakerSegment],
        label: str = "A",
        warnings: list[str] | None = None,
    ) -> "DiarizationResult":
        """
        単一話者結果を表す補助コンストラクタです。
        """
        normalized_label = label.strip().upper()
        return cls(
            segments=segments,
            speaker_count=1,
            is_single_speaker=True,
            speaker_labels=[normalized_label],
            warnings=list(warnings or []),
        )

    @classmethod
    def multi_speaker(
        cls,
        segments: list[SpeakerSegment],
        labels: list[str],
        warnings: list[str] | None = None,
    ) -> "DiarizationResult":
        """
        複数話者結果を表す補助コンストラクタです。
        """
        normalized_labels = [label.strip().upper() for label in labels]
        return cls(
            segments=segments,
            speaker_count=len(normalized_labels),
            is_single_speaker=False,
            speaker_labels=normalized_labels,
            warnings=list(warnings or []),
        )