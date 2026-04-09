class AISummarizer:
    def generate(self, audio_text, doc_text):
        # 文字起こし結果をそのまま返すだけの「仮住まい」です
        return f"【文字起こし結果】\n\n{audio_text}"