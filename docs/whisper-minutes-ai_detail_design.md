# whisper-minutes-ai 詳細設計書（初稿）

## 1. 文書の目的

本書は、Whisper編 基本設計書をもとに、`whisper-minutes-ai` の実装に直結する粒度まで詳細化した設計を定義することを目的とする。  
本書では、クラス責務、DTO、状態モデル、ジョブ状態遷移、添付資料読込、文字コード対応、各サービスの入出力契約を明確にする。

---

## 2. 対象範囲

本書の対象範囲は、Whisper編 MVP の実装に必要な詳細設計とする。

### 対象に含むもの
- クラス責務の切り分け
- クラスベース構成図
- DTO / 状態モデル
- ジョブ状態遷移
- 添付資料読込仕様
- 文字コード正規化方針
- サービス入出力契約
- フロント層との接続境界

### 対象に含まないもの
- AI補強本実装
- 人物名推論
- 高度なOCR
- TIFF本文抽出
- Excel広範囲解析

---

## 3. パッケージ構成設計

```text
whisper-minutes-ai
│
├─ front
│   ├─ WhisperAppWindow
│   ├─ MediaInputSection
│   ├─ AttachmentInputSection
│   ├─ ExecutionSection
│   ├─ ProgressSection
│   └─ ResultSection
│
├─ application
│   ├─ CreateTranscriptJobUseCase
│   ├─ ResetCurrentContextUseCase
│   ├─ LoadMediaUseCase
│   └─ AddAttachmentUseCase
│
├─ domain
│   ├─ services
│   │   ├─ SpeakerDiarizationService
│   │   ├─ TranscriptionService
│   │   ├─ AttachmentProcessingService
│   │   ├─ TranscriptFormattingService
│   │   └─ AiEnhancementService
│   │
│   ├─ models
│   │   ├─ TranscriptJob
│   │   ├─ CurrentWorkContext
│   │   ├─ TranscriptSettings
│   │   ├─ MediaFile
│   │   ├─ AttachmentFile
│   │   ├─ DiarizationResult
│   │   ├─ TranscriptionResult
│   │   ├─ FormattedTranscript
│   │   ├─ ErrorInfo
│   │   └─ JobStatus
│   │
│   └─ interfaces
│       ├─ ProgressReporter
│       ├─ JobRepository
│       ├─ TranscriptionEngine
│       ├─ DiarizationEngine
│       └─ AttachmentReader
│
├─ infrastructure
│   ├─ engines
│   │   ├─ FasterWhisperEngine
│   │   └─ WhisperXEngine
│   │
│   ├─ readers
│   │   ├─ TxtAttachmentReader
│   │   ├─ PdfAttachmentReader
│   │   ├─ ImageAttachmentReader
│   │   └─ ExcelAttachmentReader
│   │
│   ├─ repositories
│   │   └─ InMemoryJobRepository
│   │
│   └─ ui
│       └─ TkProgressReporter
│
└─ main.py
```

### 依存の向き

```text
front
  ↓
application
  ↓
domain.interfaces / domain.services / domain.models
  ↓
infrastructure
```

---

## 4. クラス責務一覧

### 4-1. front

#### `WhisperAppWindow`
- 全体ウィンドウを持つ
- 各UI部品を配置する
- ユーザー入力を受ける
- 表示を更新する
- 業務処理は持たない

#### `MediaInputSection`
- 音声/動画入力UIを担当する

#### `AttachmentInputSection`
- 補助資料の追加・一覧表示・削除UIを担当する

#### `ExecutionSection`
- 実行操作UIを担当する

#### `ProgressSection`
- 進捗表示を担当する

#### `ResultSection`
- 結果・エラー表示を担当する

### 4-2. application

#### `CreateTranscriptJobUseCase`
- 新規ジョブ生成
- 実行条件確定
- 状態遷移管理
- 進捗通知
- 各業務サービス呼び出し
- 結果集約
- エラー時失敗確定

#### `ResetCurrentContextUseCase`
- 現在状態の初期化を担当する

#### `LoadMediaUseCase`
- 主入力メディアの受理と現在状態反映を担当する

#### `AddAttachmentUseCase`
- 補助資料追加を担当する

### 4-3. domain.services

#### `SpeakerDiarizationService`
- 話者区間情報を生成する
- 単一話者/複数話者判断材料を返す

#### `TranscriptionService`
- 音声または動画から生文字起こしを生成する

#### `AttachmentProcessingService`
- 添付資料を読み、補助情報へ変換する

#### `TranscriptFormattingService`
- 最終整形済みテキストを生成する
- 単一話者時/複数話者時の出力形式を切り替える

#### `AiEnhancementService`
- 将来拡張の席
- 誤変換補正、文脈補強、要約等を担当予定

---

## 5. 依存関係設計

- `front` は `application` を呼ぶ
- `application` は業務の順序を決める
- `domain` は責務の中心である
- `infrastructure` は外部ライブラリ実装を閉じ込める
- UI は業務処理を直接呼ばない
- UseCase は GUI 具体部品を知らない
- Service は UI を知らない

---

## 6. DTO / 状態モデル設計

### 6-1. `TranscriptJob`

#### 役割
1回の実行履歴単位を表す。

#### 保持項目
- `job_id: str`
- `started_at: datetime`
- `finished_at: datetime | None`
- `media_file: MediaFile`
- `attachments: list[AttachmentFile]`
- `settings: TranscriptSettings`
- `status: JobStatus`
- `progress_phase: str`
- `progress_ratio: float`
- `attachment_read_results: list[AttachmentReadResult]`
- `attachment_supplement: AttachmentSupplement | None`
- `diarization_result: DiarizationResult | None`
- `transcription_result: TranscriptionResult | None`
- `formatted_transcript: FormattedTranscript | None`
- `error_info: ErrorInfo | None`

#### 原則
- 処理そのものは実行しない
- 状態保持の器である
- 状態変更は主に UseCase が行う

### 6-2. `CurrentWorkContext`

#### 役割
現在画面で扱っている作業コンテキストを表す。

#### 保持項目
- `current_media_file: MediaFile | None`
- `current_attachments: list[AttachmentFile]`
- `current_settings: TranscriptSettings`
- `preview_text: str`
- `progress_phase: str`
- `progress_ratio: float`
- `last_error_message: str | None`
- `active_job_id: str | None`

#### 原則
- 差し替えで消えてよい状態を保持する
- 履歴保持責務は持たない

### 6-3. `MediaFile`

#### 役割
主入力の音声/動画1件を表す。

#### 保持項目
- `media_id: str`
- `path: str`
- `file_name: str`
- `extension: str`
- `media_kind: str`
- `size_bytes: int | None`
- `selected_at: datetime`

### 6-4. `AttachmentFile`

#### 役割
補助資料1件を表す。

#### 保持項目
- `attachment_id: str`
- `path: str`
- `file_name: str`
- `extension: str`
- `media_type: str`
- `size_bytes: int | None`
- `accepted_at: datetime`

### 6-5. `TranscriptSettings`

#### 役割
実行条件の束を表す。

#### 保持項目
- `language: str`
- `enable_diarization: bool`
- `use_attachments: bool`
- `output_mode: str`
- `single_speaker_policy: str`
- `multi_speaker_label_style: str`
- `enable_ai_enhancement: bool`
- `enable_ocr: bool`
- `attachment_scope: str`

### 6-6. `JobStatus`

#### 状態一覧
- `READY`
- `ATTACHMENT_PROCESSING`
- `DIARIZING`
- `TRANSCRIBING`
- `FORMATTING`
- `COMPLETED`
- `FAILED`

---

## 7. ジョブ状態遷移設計

```text
READY
  ↓
ATTACHMENT_PROCESSING
  ↓
DIARIZING
  ↓
TRANSCRIBING
  ↓
FORMATTING
  ↓
COMPLETED
```

失敗時は任意の中間状態から `FAILED` へ遷移可能とする。

### 遷移ルール
- `READY` → `ATTACHMENT_PROCESSING`
- `ATTACHMENT_PROCESSING` → `DIARIZING`
- `DIARIZING` → `TRANSCRIBING`
- `TRANSCRIBING` → `FORMATTING`
- `FORMATTING` → `COMPLETED`
- 中間失敗 → `FAILED`

### 添付資料失敗時の扱い
- 主処理継続可能な失敗は warning または部分失敗で継続可
- 継続不能な失敗は `FAILED`
- 最終判断は `CreateTranscriptJobUseCase` が持つ

---

## 8. ユースケース処理シーケンス

### 8-1. 基本実行
1. 主入力受理
2. 新規ジョブ生成
3. 添付資料処理
4. 話者分離
5. 文字起こし
6. 整形
7. 結果返却
8. ジョブ履歴保存

### 8-2. 再実行
- 同一入力でも常に新規ジョブを生成する
- 既存ジョブは再開しない

### 8-3. 対象メディア差し替え
- 現在状態をリセットする
- ジョブ履歴は保持する

---

## 9. 添付資料読込設計

### 9-1. 目的
添付資料読込機能は、主入力に対する任意の補助情報を供給するための機能である。添付がなくてもアプリ全体は成立し、添付がある場合のみ精度補強や整形品質向上に活用する。

### 9-2. 設計上の位置づけ
- `AttachmentProcessingService` が統括する
- 実読取は `AttachmentReader` 系へ委譲する
- UI表示責務やジョブ全体進行責務は持たない

### 9-3. 対応対象
#### MVPで受理対象とする形式
- `.txt`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.tif`
- `.tiff`

#### 将来拡張対象
- `.xlsx`
- `.xls`
- `.docx`
- OCR前提の画像本文抽出
- 複数ページ画像の高度解析

### 9-4. 受理可否と活用可否の分離
- **受理**: UIがファイルを受け付け、`AttachmentFile` として登録できること
- **活用**: Reader が内容利用可能な結果を返せること

`.tif` / `.tiff` は MVP 時点で「受理可能」だが、OCR 未実装の限り「本文活用は将来拡張」とする。

### 9-5. 文字コード正規化方針
#### 対象
- `.txt`
- 将来追加されるプレーンテキスト系資料

#### 想定する文字コード
- UTF-8
- UTF-8 with BOM
- CP932 / Shift_JIS
- UTF-16

#### 読込方針
1. 読込処理は `TxtAttachmentReader` または `TextDecodingService` が担当する
2. 正常に復元できた場合のみ成功とみなす
3. 文字化けしたまま成功扱いしない
4. 判定不能または復元不能時は失敗として返す
5. 必要に応じて採用文字コードをメタ情報として保持する

### 9-6. Reader構成
- `AttachmentReader`
- `TxtAttachmentReader`
- `PdfAttachmentReader`
- `ImageAttachmentReader`
- `ExcelAttachmentReader`（将来拡張）

### 9-7. `AttachmentProcessingService` の責務
- Reader 結果を束ねる
- 後続処理用の補助情報へ変換する
- キーワード候補、固有名詞候補、会議名等の補助情報を扱う

### 9-8. 返却モデル
- `attachment_id`
- `file_name`
- `file_type`
- `accepted`
- `read_success`
- `decoded_charset`
- `extracted_text`
- `warnings`
- `errors`

### 9-9. エラー分類
- `UNSUPPORTED_EXTENSION`
- `CHARSET_DETECTION_FAILED`
- `TEXT_DECODE_FAILED`
- `PDF_READ_FAILED`
- `IMAGE_READ_FAILED`
- `OCR_NOT_IMPLEMENTED`
- `ATTACHMENT_PARSE_FAILED`

### 9-10. MVP時点の到達点
1. `.txt` / `.pdf` / 画像系ファイルを受理できる
2. `.txt` について文字コード差異を考慮して読込できる
3. 添付資料がなくてもジョブ全体は成立する
4. 添付資料の失敗内容を区別して扱える
5. `.tif` / `.tiff` を入力仕様に含める
6. `.tif` / `.tiff` の本文活用は将来拡張とする

---

## 10. 添付資料DTOおよびReader境界設計

### 10-1. DTO一覧
- `AttachmentFile`
- `AttachmentReadResult`
- `DecodedText`
- `AttachmentSupplement`
- `AttachmentError`
- `AttachmentWarning`

### 10-2. `AttachmentReadResult`
#### 保持項目
- `attachment_id: str`
- `file_name: str`
- `file_type: str`
- `accepted: bool`
- `read_success: bool`
- `decoded_charset: str | None`
- `extracted_text: str | None`
- `raw_metadata: dict[str, str] | None`
- `warnings: list[AttachmentWarning]`
- `errors: list[AttachmentError]`

### 10-3. `DecodedText`
#### 保持項目
- `text: str`
- `charset: str`
- `had_bom: bool`
- `normalization_applied: bool`
- `warnings: list[AttachmentWarning]`

### 10-4. `AttachmentSupplement`
#### 保持項目例
- `keywords: list[str]`
- `proper_noun_candidates: list[str]`
- `reference_sentences: list[str]`
- `source_attachment_ids: list[str]`

### 10-5. `AttachmentError`
#### 保持項目
- `code: str`
- `message: str`
- `detail: str | None`

### 10-6. `AttachmentWarning`
#### 保持項目
- `code: str`
- `message: str`

### 10-7. `AttachmentReader`
#### 契約
- `can_read(attachment_file: AttachmentFile) -> bool`
- `read(attachment_file: AttachmentFile) -> AttachmentReadResult`

### 10-8. `TxtAttachmentReader`
- テキスト読込を担当する
- `TextDecodingService` を内部依存として持つ

### 10-9. `PdfAttachmentReader`
- PDF本文抽出を担当する
- 高度なOCRは MVP対象外

### 10-10. `ImageAttachmentReader`
- `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff` を受理する
- MVP時点では OCR 未実装を許容する

### 10-11. `ExcelAttachmentReader`
- 将来拡張席として定義する

---

## 11. Readerインターフェース設計

### `AttachmentReader`
- `can_read()` は副作用を持たない
- `read()` は `AttachmentReadResult` を返す
- 未対応ファイルを成功扱いしない
- 可能な限り例外は DTO 上のエラーへ変換する

---

## 12. 文字コード吸収責務設計

### 12-1. `TextDecodingService`
#### 役割
テキスト系添付資料のバイト列を安全に文字列へ変換する。

#### 入力
- `raw_bytes: bytes`

#### 出力
- `DecodedText`

#### 成功条件
- 文字列として復元可能である
- 明らかな文字化けを成功扱いしない

#### 失敗条件
- 妥当な復元ができない
- 復元できても品質上不採用

### 12-2. 正規化責務
- 改行コード統一
- BOM除去
- 制御文字除去
- 前後空白調整

意味を変える変換は行わない。

---

## 13. `AttachmentProcessingService` との接続

### 入力
- `attachments: list[AttachmentFile]`

### 出力
- `list[AttachmentReadResult]`
- `AttachmentSupplement`

### 内部処理イメージ
1. 添付一覧を走査する
2. `can_read()` に合う Reader を選ぶ
3. `read()` を実行する
4. `AttachmentReadResult` を集約する
5. 成功分から `AttachmentSupplement` を生成する

---

## 14. 実装上の固定事項
- `AttachmentFile` は添付そのものを表す
- `AttachmentReadResult` は読込結果を表す
- `DecodedText` は文字コード吸収結果を表す
- `.tif` / `.tiff` は受理対象に含める
- `.tif` / `.tiff` の本文活用は OCR 導入後の将来拡張とする
- 受理可否と活用可否は分離して表現する

---

## 15. ジョブ実行ユースケース設計

### 15-1. `CreateTranscriptJobUseCase` の役割
- 新規ジョブ生成
- 実行入力確定
- ジョブ状態遷移管理
- 進捗通知
- 各サービス呼び出し
- 結果集約
- ジョブ保存
- エラー時失敗確定

### 15-2. 入力DTO `CreateTranscriptJobInput`
- `media_file: MediaFile`
- `attachments: list[AttachmentFile]`
- `settings: TranscriptSettings`

### 15-3. 出力DTO `CreateTranscriptJobOutput`
- `job_id: str`
- `status: JobStatus`
- `formatted_transcript: FormattedTranscript | None`
- `error_info: ErrorInfo | None`

---

## 16. `TranscriptJob` 設計

`TranscriptJob` は 1回の文字起こし実行処理を表す履歴側の実行単位である。

### 原則
- 実行処理はしない
- 状態保持のみ行う
- UIを知らない

---

## 17. `JobStatus` 設計

### 状態一覧
- `READY`
- `ATTACHMENT_PROCESSING`
- `DIARIZING`
- `TRANSCRIBING`
- `FORMATTING`
- `COMPLETED`
- `FAILED`

---

## 18. ジョブ状態遷移設計

### 基本遷移
```text
READY
  ↓
ATTACHMENT_PROCESSING
  ↓
DIARIZING
  ↓
TRANSCRIBING
  ↓
FORMATTING
  ↓
COMPLETED
```

### 遷移ルール
- 状態遷移は `CreateTranscriptJobUseCase` が一元管理する
- 業務サービスは状態変更してはならない

---

## 19. 進捗通知設計

### `ProgressReporter`
- `report(progress_phase: str, progress_ratio: float) -> None`

### 原則
- 進捗の意味づけは UseCase
- 進捗の描画は front

---

## 20. `CreateTranscriptJobUseCase` の処理シーケンス

1. `CreateTranscriptJobInput` を受理する
2. 新規 `TranscriptJob` を生成する
3. `JobRepository` に初期保存する
4. 進捗通知を行う
5. 添付資料処理を実行する
6. 話者分離を実行する
7. 文字起こしを実行する
8. 整形を実行する
9. `COMPLETED` へ遷移する
10. 最終保存する
11. `CreateTranscriptJobOutput` を返す

### 失敗時
- `error_info` を生成する
- `status=FAILED` を設定する
- 終了時刻を設定する
- 保存する
- 失敗進捗通知を行う
- 失敗結果を返す

---

## 21. UseCase 内部依存

### 依存先
- `JobRepository`
- `ProgressReporter`
- `AttachmentProcessingService`
- `SpeakerDiarizationService`
- `TranscriptionService`
- `TranscriptFormattingService`

### 依存しないもの
- `FasterWhisperEngine`
- `WhisperXEngine`
- GUI具体部品
- `TextDecodingService`
- `AttachmentReader` の具体実装

---

## 22. `JobRepository` 設計

### 契約
- `save(job: TranscriptJob) -> None`
- `find_by_id(job_id: str) -> TranscriptJob | None`
- `list_all() -> list[TranscriptJob]`

### MVP実装
- `InMemoryJobRepository`

---

## 23. `TranscriptFormattingService` 入力契約補強

### 入力
- `transcription_result: TranscriptionResult`
- `diarization_result: DiarizationResult | None`
- `attachment_supplement: AttachmentSupplement | None`
- `settings: TranscriptSettings`

### 出力
- `FormattedTranscript`

### 整形責務
- 単一話者時は冒頭に話者情報ブロックを付与する
- 複数話者時は A/B/C ラベル付き本文へ整形する
- 人物名推論は行わない

---

## 24. 実装上の固定事項
- 文字起こし実行1回 = 1 `TranscriptJob`
- 状態遷移は UseCase が一元管理する
- 添付資料処理は独立状態を持つ
- 添付資料の部分失敗と継続を表現可能にする
- `ProgressReporter` は進捗通知境界である
- `JobRepository` はジョブ保存境界である

---

## 25. 現在状態設計

### `CurrentWorkContext` の役割
現在フロント層が扱っている作業コンテキストを表す。

### 保持するもの
- 現在選択中の主入力
- 現在添付中の補助資料
- 現在有効な設定
- 現在表示中の進捗
- 現在表示中の結果
- 現在発生している表示用エラー
- 現在関連づいているアクティブジョブID

---

## 26. `MediaFile` / `TranscriptSettings` 設計

### `MediaFile`
主入力1件を表す DTO。

### `TranscriptSettings`
実行条件の束を表す DTO。ジョブ入力確定時点でスナップショット化される。

---

## 27. 現在状態ユースケース設計

### `LoadMediaUseCase`
- 主入力メディアを受理し、現在状態へ反映する

### `AddAttachmentUseCase`
- 補助資料を現在状態へ追加する

### `ResetCurrentContextUseCase`
- 現在状態を初期化する

---

## 28. 対象メディア差し替え設計

### 差し替え時のルール
1. 古い現在状態を破棄する
2. 添付資料を初期化する
3. 表示中結果を初期化する
4. エラー表示を初期化する
5. 進捗表示を初期化する
6. 新しい主入力を設定する

### ジョブ履歴との関係
差し替え前のジョブ履歴は保持する。

---

## 29. フロント接続境界設計

### フロント → アプリケーション層
- 主入力選択時: `LoadMediaUseCase.execute(...)`
- 添付資料追加時: `AddAttachmentUseCase.execute(...)`
- 実行時: `CreateTranscriptJobUseCase.execute(...)`
- リセット時: `ResetCurrentContextUseCase.execute(...)`

### フロントが直接触らないもの
- `TranscriptionService`
- `SpeakerDiarizationService`
- `AttachmentProcessingService`
- `TranscriptFormattingService`
- `JobRepository`
- `AttachmentReader`
- 外部ライブラリ実装

---

## 30. 実行可能判定設計

### 基本条件
- `current_media_file is not None`
- 現在実行中でない
- 必須入力不備がない
- 重大な現在状態エラーがない

### 添付資料
0件でも実行可能とする。

---

## 31. 多重実行防止設計

- `active_job_id` が存在し、対応ジョブが未完了である間は新規実行を禁止する
- front 側は実行中に実行ボタンを無効化する
- application 側でも二重起動を検知可能にする

---

## 32. 再実行設計

- 再実行時も常に新規 `TranscriptJob` を生成する
- 既存ジョブを再開しない
- `CurrentWorkContext` をもとに再度 `CreateTranscriptJobInput` を構築する

---

## 33. `CurrentWorkContext` と `TranscriptJob` の境界再確認

### `CurrentWorkContext`
- 今の画面状態
- 差し替えで消える
- 実行前/実行中の表示都合を持つ

### `TranscriptJob`
- 1回の実行履歴
- 完了後も残る
- 入力・中間結果・最終結果・失敗情報を持つ

---

## 34. 詳細設計としての固定事項
- `CurrentWorkContext` は現在画面状態を表す
- `TranscriptJob` は履歴側実行単位を表す
- 主入力差し替え時は現在状態をリセットする
- ジョブ履歴は差し替えでも保持する
- 多重起動は防止する
- 再実行は毎回新規ジョブである

---

## 35. サービス入出力DTO統一設計

### 対象DTO
- `DiarizationResult`
- `SpeakerSegment`
- `TranscriptionResult`
- `TranscriptSegment`
- `FormattedTranscript`
- `ErrorInfo`

### 基本原則
- 各サービスは自分の責務範囲に対応した DTO を返す
- DTO は状態を表す器である
- UI表示用文字列と結果DTOを混同しない

---

## 36. `DiarizationResult` 設計

### 保持項目
- `segments: list[SpeakerSegment]`
- `speaker_count: int`
- `is_single_speaker: bool`
- `speaker_labels: list[str]`
- `raw_metadata: dict[str, str] | None`
- `warnings: list[str]`

### `SpeakerSegment`
- `start_sec: float`
- `end_sec: float`
- `speaker_label: str`

### 原則
- 人物名は持たない
- ラベルは `A/B/C...` の抽象ラベルに留める

---

## 37. `TranscriptionResult` 設計

### 保持項目
- `full_text: str`
- `segments: list[TranscriptSegment]`
- `language: str`
- `duration_sec: float | None`
- `raw_metadata: dict[str, str] | None`
- `warnings: list[str]`

### `TranscriptSegment`
- `start_sec: float`
- `end_sec: float`
- `text: str`
- `speaker_label: str | None`

### 原則
- 最終段落整形をしない
- 単一話者時の冒頭ブロック付与をしない
- 本文ラベル整形をしない

---

## 38. `FormattedTranscript` 設計

### 保持項目
- `text: str`
- `speaker_mode: str`
- `speaker_labels_used: list[str]`
- `source_job_id: str | None`
- `warnings: list[str]`

### 原則
- 単一話者時は冒頭ブロックを付与する
- 複数話者時は本文に `話者A:` 形式を付与する
- 人物名推論は行わない

---

## 39. `ErrorInfo` 設計

### 保持項目
- `code: str`
- `message: str`
- `detail: str | None`
- `failed_phase: str | None`
- `exception_type: str | None`

### 想定コード
- `MEDIA_NOT_FOUND`
- `INVALID_INPUT`
- `ATTACHMENT_PROCESSING_FAILED`
- `DIARIZATION_FAILED`
- `TRANSCRIPTION_FAILED`
- `FORMATTING_FAILED`
- `INTERNAL_ERROR`

---

## 40. サービス入出力契約

### `SpeakerDiarizationService`
#### 入力
- `media_file: MediaFile`
- `settings: TranscriptSettings`

#### 出力
- `DiarizationResult`

### `TranscriptionService`
#### 入力
- `media_file: MediaFile`
- `settings: TranscriptSettings`

#### 出力
- `TranscriptionResult`

### `AttachmentProcessingService`
#### 入力
- `attachments: list[AttachmentFile]`

#### 出力
- `tuple[list[AttachmentReadResult], AttachmentSupplement | None]`

### `TranscriptFormattingService`
#### 入力
- `transcription_result: TranscriptionResult`
- `diarization_result: DiarizationResult | None`
- `attachment_supplement: AttachmentSupplement | None`
- `settings: TranscriptSettings`

#### 出力
- `FormattedTranscript`

---

## 41. `TranscriptJob` への反映方針

- 添付資料処理結果 → `attachment_read_results`, `attachment_supplement`
- 話者分離結果 → `diarization_result`
- 文字起こし結果 → `transcription_result`
- 整形結果 → `formatted_transcript`

DTO の生成は各サービス、ジョブ反映は UseCase、保存は Repository が担う。

---

## 42. DTO相互関係整理

```text
MediaFile / AttachmentFile / TranscriptSettings
          ↓
CreateTranscriptJobInput
          ↓
AttachmentProcessingService → AttachmentReadResult / AttachmentSupplement
SpeakerDiarizationService   → DiarizationResult
TranscriptionService        → TranscriptionResult
TranscriptFormattingService → FormattedTranscript
          ↓
TranscriptJob
          ↓
CreateTranscriptJobOutput
```

---

## 43. DTO命名規約

### 原則
- ファイルそのもの → `*File`
- 実行設定 → `*Settings`
- 実行要求 → `*Input`
- 実行応答 → `*Output`
- 読込/解析結果 → `*Result`
- 最終成果物 → `Formatted*`
- エラー → `*Error` / `ErrorInfo`

### 避けること
- `Data`, `Info`, `Object` のような広すぎる命名
- DTO なのに副作用を持つクラス
- DTO なのに他層を知るクラス

---

## 44. 詳細設計としての固定事項

- 話者分離結果は `DiarizationResult`
- 文字起こし結果は `TranscriptionResult`
- 最終整形結果は `FormattedTranscript`
- ジョブ全体失敗は `ErrorInfo`
- DTO は状態保持の器であり、処理責務を持ちすぎない
- `TranscriptJob` への反映は UseCase が担う
- 人物名推論は DTO にも含めない

---

## 45. 次工程への引き継ぎ

本書の次工程では、以下を実装対象とする。

- DTO の dataclass 化
- `Protocol` / interface 化
- `main.py` の DI 配線設計
- `InMemoryJobRepository` の実装
- `TextDecodingService` の実装
- `CreateTranscriptJobUseCase` の骨組み実装
- `WhisperAppWindow` と UseCase の接続

