import os, glob, json, gzip

SAVE_DIR = "Fake"

json_files = glob.glob(os.path.join(SAVE_DIR, "*.json"))

for f in json_files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
        gz_file = f"{f}.gz"
        with gzip.open(gz_file, "wt", encoding="utf-8") as gz:
            json.dump(data, gz, ensure_ascii=False, separators=(',',':'))
        os.remove(f)  
        print(f"Compressed {f} -> {gz_file}")
    except Exception as e:
        print(f"Failed to compress {f}: {e}")
