import os

def save_text(text, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)