import customtkinter as ctk
from tkinter import filedialog
import threading

class WhisperMinutesApp(ctk.CTk):
    def __init__(self, transcriber, doc_processor, summarizer):
        super().__init__()
        
        # 依存性の注入（DI）
        self._transcriber = transcriber
        self._doc_processor = doc_processor
        self._summarizer = summarizer

        # 選択されたパスを保持
        self.selected_audio_path = None
        self.selected_docs_path = None

        # --- ウィンドウ設定 ---
        self.title("whisper-minutes-ai v0.2")
        self.geometry("700x800") # 少し縦長に広げました
        
        # 全体のレイアウト設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # 結果表示エリアを伸縮可能に

        # --- 上段：音声・動画入力エリア (常にEnable) ---
        self.audio_frame = ctk.CTkFrame(self)
        self.audio_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        self.audio_label = ctk.CTkLabel(self.audio_frame, text="【上段】音声・動画ファイル (.mp3, .mp4など)", font=("Arial", 16))
        self.audio_label.pack(pady=10)
        
        self.audio_btn = ctk.CTkButton(self.audio_frame, text="ファイルを選択", command=self.select_audio)
        self.audio_btn.pack(pady=10)
        
        self.audio_path_label = ctk.CTkLabel(self.audio_frame, text="未選択", text_color="gray", wraplength=500)
        self.audio_path_label.pack(padx=10)

        # --- 下段：追加資料エリア (初期はDisable) ---
        self.docs_frame = ctk.CTkFrame(self)
        self.docs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.docs_label = ctk.CTkLabel(self.docs_frame, text="【下段】追加資料 (.pdf, .txtなど)", font=("Arial", 16), text_color="gray")
        self.docs_label.pack(pady=10)
        
        self.docs_btn = ctk.CTkButton(self.docs_frame, text="ファイルを選択", state="disabled", command=self.select_docs)
        self.docs_btn.pack(pady=10)
        
        self.docs_path_label = ctk.CTkLabel(self.docs_frame, text="未選択", text_color="gray", wraplength=500)
        self.docs_path_label.pack(padx=10)

        # --- 文字起こし結果表示エリア ---
        self.result_label = ctk.CTkLabel(self, text="【結果】文字起こし内容", font=("Arial", 14))
        self.result_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.result_box = ctk.CTkTextbox(self, font=("Arial", 12), border_width=2)
        self.result_box.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")

        # --- 進捗エリア ---
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="上段のファイルを選んでくださいな🌸", font=("Arial", 12))
        self.progress_label.pack(pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(padx=20, pady=10, fill="x")
        self.progress_bar.set(0)

        # --- 実行ボタン (初期はDisable) ---
        self.run_btn = ctk.CTkButton(self, text="議事録作成を開始する", fg_color="gray", state="disabled", command=self.start_process)
        self.run_btn.grid(row=5, column=0, pady=20)

    # --- メソッド群 ---
    def select_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio/Video", "*.mp3 *.wav *.m4a *.mp4 *.mov")])
        if file_path:
            self.selected_audio_path = file_path
            self.audio_path_label.configure(text=file_path, text_color="white")
            
            # 開放連鎖です！
            self.docs_btn.configure(state="normal")
            self.docs_label.configure(text_color="white")
            self.run_btn.configure(state="normal", fg_color="#2fa572") # 鮮やかな緑
            self.progress_label.configure(text="準備が整いましたわ🌸")

    def select_docs(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.txt *.docx *.png *.jpg")])
        if file_path:
            self.selected_docs_path = file_path
            self.docs_path_label.configure(text=file_path, text_color="white")

    def update_progress(self, value, message):
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
        self.update_idletasks()

    def start_process(self):
        # 多重実行防止と画面クリア
        self.run_btn.configure(state="disabled")
        self.result_box.delete("0.0", "end")
        
        thread = threading.Thread(target=self.run_task, daemon=True)
        thread.start()

    def run_task(self):
        try:
            # 文字起こし実行
            text = self._transcriber.run(self.selected_audio_path, self.update_progress)
            
            # 結果をテキストエリアに表示
            self.result_box.insert("0.0", text)
            
        except Exception as e:
            self.update_progress(0, f"エラーが発生してしまいました：{e}")
        finally:
            self.run_btn.configure(state="normal")