import os
import whisper
import ctypes
from pathlib import Path

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self._model = None

    def get_short_path(self, long_path):
        """Windowsの空白を含むパスを、絶対にちぎれない短いパス形式に変換しますわ🌸"""
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, 260)
        return buf.value

    def run(self, file_path, progress_callback):
        try:
            # 生成した「最強のパス」をそのまま使います！
            abs_path = os.path.abspath(file_path)
            buf = ctypes.create_unicode_buffer(260)
            ctypes.windll.kernel32.GetShortPathNameW(abs_path, buf, 260)
            safe_short_path = buf.value

            # もしモデルがまだ読み込まれていなければ、ここでしっかり呼び起こします
            if self._model is None:
                progress_callback(0.2, "Whisperモデルを呼び起こしています...")
                # ここでモデルをロードします！
                self._model = whisper.load_model(self.model_size)
            
            progress_callback(0.5, "ついに、言葉を聴き取ります...！💫")
            
            # ✨ 物理的に最強なパスで、文字起こしを開始します！
            result = self._model.transcribe(safe_short_path, verbose=False)
            
            return result["text"]

        except Exception as e:
            raise Exception(f"あと一歩...！：{e}")