import os
import whisper
import ctypes
from pathlib import Path
from faster_whisper import WhisperModel

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
        
        
        

class FasterWhisperTranscriber:
    def __init__(self):
        # なぜ:
        #   議事録用途では、まず精度優先で large-v3 系を基準に置く。
        #   CPU なら int8、GPU なら float16 / int8_float16 が現実的。
        self.model = WhisperModel(
            "large-v3",
            device="cpu",          # GPU なら "cuda"
            compute_type="int8"    # GPU なら "float16" など
        )

    def run(self, audio_path, progress_callback):
        progress_callback(0.05, "音声を解析する準備をしております…")

        # なぜ:
        #   日本語を明示すると誤言語判定を減らしやすい。
        #   beam_size は安定重視の無難な設定。
        #   vad_filter で無音を削る。
        #   word_timestamps=True は後段の整形・話者分離と相性がよい。
        segments, info = self.model.transcribe(
            audio_path,
            language="ja",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            word_timestamps=True,
            condition_on_previous_text=False,
            initial_prompt=(
                "これは日本語の会議音声です。"
                "固有名詞、製品名、英単語混じりの専門用語をそのまま書き起こしてください。"
                "不要な意訳はせず、話し言葉に忠実に転写してください。"
            )
        )

        progress_callback(0.4, "文字起こしを進めております…")

        lines = []
        segments = list(segments)  # generator をここで確定

        total = max(len(segments), 1)
        for i, seg in enumerate(segments, start=1):
            lines.append(seg.text.strip())
            progress_callback(0.4 + 0.5 * i / total, f"整形中… {i}/{total}")

        progress_callback(1.0, "文字起こしが完了いたしましたわ🌸")
        return "\n".join(line for line in lines if line)