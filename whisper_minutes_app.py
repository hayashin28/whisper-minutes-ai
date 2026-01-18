import customtkinter as ctk
from tkinter import filedialog

class WhisperMinutesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- ウィンドウの設定 ---
        self.title("whisper-minutes-ai - Prototype v0.1")
        self.geometry("600x550")
        
        # 全体のレイアウト設定（3行構成：上段、下段、ボタン）
        self.grid_rowconfigure(0, weight=1) # 上段
        self.grid_rowconfigure(1, weight=1) # 下段
        self.grid_rowconfigure(2, weight=0) # 実行ボタン（固定幅）
        self.grid_columnconfigure(0, weight=1)

        # --- 上段：音声・動画入力エリア ---
        self.audio_frame = ctk.CTkFrame(self)
        self.audio_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        self.audio_label = ctk.CTkLabel(self.audio_frame, text="【上段】音声・動画ファイル (.mp3, .mp4など)", font=("Arial", 16))
        self.audio_label.pack(pady=10)
        
        self.audio_btn = ctk.CTkButton(self.audio_frame, text="ファイルを選択", command=self.select_audio)
        self.audio_btn.pack(pady=10)
        
        self.audio_path_label = ctk.CTkLabel(self.audio_frame, text="未選択", text_color="gray")
        self.audio_path_label.pack()

        # --- 下段：追加資料エリア ---
        self.docs_frame = ctk.CTkFrame(self)
        self.docs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.docs_label = ctk.CTkLabel(self.docs_frame, text="【下段】追加資料 (.pdf, .txtなど)", font=("Arial", 16))
        self.docs_label.pack(pady=10)
        
        self.docs_btn = ctk.CTkButton(self.docs_frame, text="ファイルを選択", command=self.select_docs)
        self.docs_btn.pack(pady=10)
        
        self.docs_path_label = ctk.CTkLabel(self.docs_frame, text="未選択", text_color="gray")
        self.docs_path_label.pack()

        # --- 最下部：実行ボタン ---
        # ここも grid に変更しましたわ！✨
        self.run_btn = ctk.CTkButton(self, text="議事録作成を開始する", fg_color="green", hover_color="darkgreen")
        self.run_btn.grid(row=2, column=0, pady=20)

    def select_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio/Video", "*.mp3 *.wav *.m4a *.mp4 *.mov")])
        if file_path:
            self.audio_path_label.configure(text=file_path, text_color="white")

    def select_docs(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.txt *.docx *.png *.jpg")])
        if file_path:
            self.docs_path_label.configure(text=file_path, text_color="white")

if __name__ == "__main__":
    app = WhisperMinutesApp()
    app.mainloop()