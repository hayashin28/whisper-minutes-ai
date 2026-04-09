import sys
import os

# 自作モジュールを読み込めるようにパスを通します
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.transcriber import WhisperTranscriber
# ※ まだ中身が空でも、クラスの定義だけあれば動きます🌸
from app import WhisperMinutesApp

# 今後のために仮のクラスを置いておきますね
class DocumentProcessor: pass
class AISummarizer: pass

def main():
    # 1. 具象クラス（実体）の生成
    # ここで設定値（モデルサイズなど）を渡すのも、DIの美しいところです✨
    transcriber = WhisperTranscriber(model_size="base")
    doc_processor = DocumentProcessor()
    summarizer = AISummarizer()

    # 2. DI（依存性の注入）！
    # Appは、中身がどう動くか知らなくても、これらを使えばいいことだけを知っています
    app = WhisperMinutesApp(
        transcriber=transcriber,
        doc_processor=doc_processor,
        summarizer=summarizer
    )
    
    # 3. 起動
    print("whisper-minutes-ai を起動します🌸")
    app.mainloop()

if __name__ == "__main__":
    main()