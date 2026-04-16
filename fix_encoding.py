import os

def fix_encoding_strict(file_path):
    try:
        # 1. まずバイナリで読み込みます
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # 2. 文字化け（UTF-8で化けている状態）を検出するためのロジック
        # UTF-8でデコードしたときに、特定の化け文字（縺、縏、繧など）が
        # 含まれている場合は、Shift-JISとして読み直します
        try:
            content = raw_data.decode('utf-8')
            # 簡易的な文字化け判定（UTF-8として読めるが意味不明な漢字が並んでいる場合）
            if "縺" in content or "繧" in content or "縏" in content:
                raise UnicodeDecodeError("utf-8", raw_data, 0, 1, "custom check: looks like garbled text")
        except UnicodeDecodeError:
            # Shift-JIS (cp932) として読み込み
            content = raw_data.decode('cp932', errors='replace')

        # 3. UTF-8（BOMなし）で完全に上書きします
        # 確実にOSのキャッシュをクリアするために、一度内容を空にしてから書き込みます
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
            
        return True
    except Exception as e:
        print(f"エラー: {file_path} -> {e}")
        return False

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"=== 強化版・修復を開始します！ ===")
    
    found_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".py") and file != os.path.basename(__file__):
                found_files.append(os.path.join(root, file))

    success_count = 0
    for path in found_files:
        rel_path = os.path.relpath(path, root_dir)
        if fix_encoding_strict(path):
            print(f"修復・確認済み: {rel_path}")
            success_count += 1

    print(f"==============================")
    print(f"完了しました！ {success_count}個のファイルを更新しました。")
    print("一度エディタを閉じて開き直してみてください。")
    input("\nEnterキーで終了します...")

if __name__ == "__main__":
    main()