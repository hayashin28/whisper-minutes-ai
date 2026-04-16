from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TranscriptSegment:
    """
    文字起こし結果の1区間を表すDTO。

    なぜ:
        時間軸つきの転写結果を後続へ渡せるようにするためです。
        将来的に話者ラベルとの突合や、区間単位の整形にも使えます。

    前提:
        この段階では、speaker_label は未設定でも構いません。
        話者分離結果との突合後に埋まる可能性があります。
    """

    start_sec: float
    end_sec: float
    text: str
    speaker_label: str | None = None

    def __post_init__(self) -> None:
        normalized_text = self.text.strip()
        normalized_speaker_label = self.speaker_label.strip().upper() if self.speaker_label else None

        if self.start_sec < 0:
            raise ValueError("start_sec は 0 以上で指定してください。")

        if self.end_sec < 0:
            raise ValueError("end_sec は 0 以上で指定してください。")

        if self.end_sec < self.start_sec:
            raise ValueError("end_sec は start_sec 以上で指定してください。")

        if not normalized_text:
            raise ValueError("text は空にできません。")

        object.__setattr__(self, "text", normalized_text)
        object.__setattr__(self, "speaker_label", normalized_speaker_label)


@dataclass(frozen=True)
class TranscriptionResult:
    """
    生の文字起こし結果を表すDTO。

    なぜ:
        音声認識結果そのものと、最終整形済み出力を分離するためです。
        これにより、文字起こし責務と整形責務を混同しないようにします。

    前提:
        ここでは最終段落整形や話者A/B/Cの見た目調整は行いません。
        あくまで転写結果の保持に留めます。
    """

    full_text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str = "ja"
    duration_sec: float | None = None
    raw_metadata: dict[str, str] | None = None
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized_full_text = self.full_text.strip()
        normalized_language = self.language.strip().lower()

        if not normalized_full_text:
            raise ValueError("full_text は空にできません。")

        if not normalized_language:
            raise ValueError("language は空にできません。")

        if self.duration_sec is not None and self.duration_sec < 0:
            raise ValueError("duration_sec は 0 以上、または None を指定してください。")

        object.__setattr__(self, "full_text", normalized_full_text)
        object.__setattr__(self, "language", normalized_language)

    @classmethod
    def empty(cls, language: str = "ja") -> "TranscriptionResult":
        """
        まだ有効な転写結果が無い状態を表す補助コンストラクタです。

        注意:
            full_text を空にできない設計なので、
            空結果用に最小のプレースホルダ文字列を入れます。
            本実装接続後は、必要に応じて見直しても構いません。
        """
        return cls(
            full_text="[EMPTY_TRANSCRIPTION]",
            segments=[],
            language=language,
            duration_sec=None,
            warnings=["empty_transcription_result"],
        )

    @classmethod
    def from_text(
        cls,
        full_text: str,
        language: str = "ja",
        duration_sec: float | None = None,
        warnings: list[str] | None = None,
    ) -> "TranscriptionResult":
        """
        区間情報なしの単純な文字起こし結果を作る補助コンストラクタです。
        """
        return cls(
            full_text=full_text,
            segments=[],
            language=language,
            duration_sec=duration_sec,
            warnings=list(warnings or []),
        )