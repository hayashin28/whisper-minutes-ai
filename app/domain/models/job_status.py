from enum import Enum


class JobStatus(str, Enum):
    """
    文字起こしジョブの状態を表す列挙型。

    なぜ:
        ジョブ状態を文字列の打ち間違いから守るためです。
        また、UseCase・DTO・UI のあいだで同じ語彙を共有するためです。

    前提:
        状態遷移の管理責務は UseCase 側にあり、
        この Enum 自体は「状態名」を定義するだけに留めます。

    入出力:
        入力はありません。
        各メンバーが状態値を表します。

    副作用:
        ありません。

    例外:
        ありません。
    """

    READY = "READY"
    ATTACHMENT_PROCESSING = "ATTACHMENT_PROCESSING"
    DIARIZING = "DIARIZING"
    TRANSCRIBING = "TRANSCRIBING"
    FORMATTING = "FORMATTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"