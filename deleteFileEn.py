import gzip
import json
import os

def check_and_delete(file_path, lang_key="language"):
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)

        lang = str(data.get(lang_key, "")).lower()

        if lang in ["english", "en"]:
            os.remove(file_path)
            print(f"Deleted {file_path} (language: {lang})")
        else:
            print(f"Kept {file_path} (language: {lang})")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


def process_directory(folder_path, lang_key="language"):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json.gz"):
            file_path = os.path.join(folder_path, filename)
            check_and_delete(file_path, lang_key)


process_directory("Real", lang_key="en")
