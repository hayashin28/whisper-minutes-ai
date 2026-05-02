from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from app.application.create_transcript_job_usecase import (
    CreateTranscriptJobInput,
    CreateTranscriptJobUseCase,
)
from app.domain.models.current_work_context import CurrentWorkContext
from app.domain.models.media_file import MediaFile


class WhisperAppWindow(ctk.CTk):
    """
    whisper-minutes-ai の最小ウィンドウです。

    この段階では、
    - 主入力ファイルの選択
    - CurrentWorkContext への反映
    - 実行可否に応じたボタン制御
    - 実行ボタンから UseCase 呼び出し
    - 進捗表示
    - 結果表示
    までを担当します。
    """

    def __init__(self) -> None:
        super().__init__()

        self._create_transcript_job_usecase: CreateTranscriptJobUseCase | None = None
        self._current_work_context = CurrentWorkContext()

        self.title("whisper-minutes-ai")
        self.geometry("900x760")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_layout()
        self._refresh_view_state()

    def set_create_transcript_job_usecase(
        self,
        create_transcript_job_usecase: CreateTranscriptJobUseCase,
    ) -> None:
        """
        main.py 側で生成した UseCase を後から注入します。
        """
        self._create_transcript_job_usecase = create_transcript_job_usecase

    def _build_layout(self) -> None:
        root_frame = ctk.CTkFrame(self)
        root_frame.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")

        root_frame.grid_columnconfigure(0, weight=1)
        root_frame.grid_rowconfigure(5, weight=1)

        title_label = ctk.CTkLabel(
            root_frame,
            text="whisper-minutes-ai",
            font=("Arial", 24, "bold"),
        )
        title_label.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        description_label = ctk.CTkLabel(
            root_frame,
            text="文字起こしアプリの最小起動確認です。",
            font=("Arial", 14),
        )
        description_label.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        self._build_media_input_section(root_frame)
        self._build_execution_section(root_frame)
        self._build_progress_section(root_frame)
        self._build_result_section(root_frame)

    def _build_media_input_section(self, parent: ctk.CTkFrame) -> None:
        media_frame = ctk.CTkFrame(parent)
        media_frame.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        media_frame.grid_columnconfigure(0, weight=1)

        media_title_label = ctk.CTkLabel(
            media_frame,
            text="主入力（音声/動画）",
            font=("Arial", 18, "bold"),
        )
        media_title_label.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        media_select_button = ctk.CTkButton(
            media_frame,
            text="ファイルを選択",
            command=self._on_select_media_file,
        )
        media_select_button.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self._media_path_label = ctk.CTkLabel(
            media_frame,
            text="未選択",
            font=("Arial", 13),
            anchor="w",
            justify="left",
        )
        self._media_path_label.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _build_execution_section(self, parent: ctk.CTkFrame) -> None:
        execution_frame = ctk.CTkFrame(parent)
        execution_frame.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="ew")
        execution_frame.grid_columnconfigure(0, weight=1)

        execution_title_label = ctk.CTkLabel(
            execution_frame,
            text="実行",
            font=("Arial", 18, "bold"),
        )
        execution_title_label.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self._execute_button = ctk.CTkButton(
            execution_frame,
            text="文字起こしを開始",
            command=self._on_execute,
            state="disabled",
        )
        self._execute_button.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self._execution_hint_label = ctk.CTkLabel(
            execution_frame,
            text="主入力ファイルを選ぶと実行できます。",
            font=("Arial", 13),
            anchor="w",
            justify="left",
        )
        self._execution_hint_label.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _build_progress_section(self, parent: ctk.CTkFrame) -> None:
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.grid(row=4, column=0, padx=16, pady=(0, 16), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        progress_title_label = ctk.CTkLabel(
            progress_frame,
            text="進捗",
            font=("Arial", 18, "bold"),
        )
        progress_title_label.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self._progress_phase_label = ctk.CTkLabel(
            progress_frame,
            text="未実行",
            font=("Arial", 13),
            anchor="w",
            justify="left",
        )
        self._progress_phase_label.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")

        self._progress_bar = ctk.CTkProgressBar(progress_frame)
        self._progress_bar.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        self._progress_bar.set(0.0)

    def _build_result_section(self, parent: ctk.CTkFrame) -> None:
        result_frame = ctk.CTkFrame(parent)
        result_frame.grid(row=5, column=0, padx=16, pady=(0, 16), sticky="nsew")
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(1, weight=1)

        result_title_label = ctk.CTkLabel(
            result_frame,
            text="結果",
            font=("Arial", 18, "bold"),
        )
        result_title_label.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self._result_textbox = ctk.CTkTextbox(
            result_frame,
            font=("Arial", 13),
        )
        self._result_textbox.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self._result_textbox.insert("0.0", "ここに文字起こし結果を表示します。")
        self._result_textbox.configure(state="disabled")

    def _on_select_media_file(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="音声または動画ファイルを選択",
            filetypes=[
                ("Audio / Video", "*.mp3 *.wav *.m4a *.mp4 *.mov *.mkv"),
                ("All files", "*.*"),
            ],
        )

        if not selected_path:
            return

        media_kind = self._infer_media_kind(selected_path)
        selected_file = Path(selected_path)

        media_file = MediaFile(
            media_id=f"media-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            path=selected_path,
            file_name=selected_file.name,
            extension=selected_file.suffix.lower(),
            media_kind=media_kind,
            size_bytes=selected_file.stat().st_size if selected_file.exists() else None,
            selected_at=datetime.now(),
        )

        self._current_work_context.reset_for_media_replacement()
        self._current_work_context.current_media_file = media_file
        self._refresh_view_state()

    def _on_execute(self) -> None:
        media_file = self._current_work_context.current_media_file
        if media_file is None:
            self._execution_hint_label.configure(text="主入力ファイルが未選択です。")
            return

        if self._create_transcript_job_usecase is None:
            self._execution_hint_label.configure(text="UseCase が未配線です。")
            return

        self._current_work_context.active_job_id = "running"
        self._refresh_view_state()
        self._execution_hint_label.configure(text="実行中です。")
        self._set_result_text("文字起こしを実行しています...")
        self._update_progress("開始", 0.0)

        try:
            input_data = CreateTranscriptJobInput(
                media_file=media_file,
                attachments=list(self._current_work_context.current_attachments),
                settings=self._current_work_context.current_settings,
            )

            output_data = self._create_transcript_job_usecase.execute(input_data)
            status_text = f"status: {output_data.status.value}"

            if output_data.error_info is not None:
                self._current_work_context.last_error_message = output_data.error_info.message
                self._execution_hint_label.configure(
                    text=f"失敗しました: {output_data.error_info.message}"
                )
                self._set_result_text(
                    f"{status_text}\n\n"
                    f"error_code: {output_data.error_info.code}\n"
                    f"message: {output_data.error_info.message}\n"
                    f"detail: {output_data.error_info.detail}"
                )
            else:
                self._execution_hint_label.configure(
                    text=f"完了しました。job_id={output_data.job_id}"
                )

                if output_data.formatted_transcript is not None:
                    self._set_result_text(output_data.formatted_transcript.text)
                else:
                    self._set_result_text(
                        f"{status_text}\n\n"
                        f"job_id: {output_data.job_id}\n"
                        "整形済み本文は取得できませんでした。"
                    )

        except Exception as exc:
            self._current_work_context.last_error_message = str(exc)
            self._execution_hint_label.configure(
                text="実行中に予期しない例外が発生しました。"
            )
            self._set_result_text(
                "実行中に予期しない例外が発生しました。\n\n"
                f"{type(exc).__name__}: {exc}"
            )

        finally:
            self._current_work_context.active_job_id = None
            self._refresh_view_state()

    def handle_progress_update(self, progress_phase: str, progress_ratio: float) -> None:
        """
        ProgressReporter から受けた進捗を UI に反映します。
        """
        self._update_progress(progress_phase, progress_ratio)

    def _update_progress(self, progress_phase: str, progress_ratio: float) -> None:
        clamped_ratio = max(0.0, min(1.0, progress_ratio))
        self._progress_phase_label.configure(text=progress_phase)
        self._progress_bar.set(clamped_ratio)
        self.update_idletasks()

    def _refresh_view_state(self) -> None:
        media_file = self._current_work_context.current_media_file

        if media_file is None:
            self._media_path_label.configure(text="未選択")
        else:
            self._media_path_label.configure(text=f"選択中: {media_file.path}")

        if self._current_work_context.can_execute():
            self._execute_button.configure(state="normal")
            if self._current_work_context.last_error_message is None:
                self._execution_hint_label.configure(
                    text="主入力が選択済みです。実行できます。"
                )
        else:
            self._execute_button.configure(state="disabled")
            if self._current_work_context.active_job_id is None:
                self._execution_hint_label.configure(
                    text="主入力ファイルを選ぶと実行できます。"
                )

    def _set_result_text(self, text: str) -> None:
        self._result_textbox.configure(state="normal")
        self._result_textbox.delete("0.0", "end")
        self._result_textbox.insert("0.0", text)
        self._result_textbox.configure(state="disabled")

    def _infer_media_kind(self, path: str) -> str:
        extension = Path(path).suffix.lower()

        if extension in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
            return "audio"

        return "video"