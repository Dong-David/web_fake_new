import pandas as pd
import json, gzip, os
import hashlib

CSV_FILE = "Fake.csv"        
OUTPUT_DIR = "Fake"    
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)

existing_hashes = set()  
for i, row in df.iterrows():
    title = str(row['title'])
    text = str(row['text'])
    subject = str(row.get('subject', 'unknown'))
    date = str(row.get('date', 'unknown'))
    
    article_hash = hashlib.md5((title + text).encode('utf-8')).hexdigest()
    if article_hash in existing_hashes:
        continue
    
    article = {
        "title": title,
        "text": text,
        "subject": subject,
        "date": date,
        "url": f"real://article{i}"
    }
    
    file_name = os.path.join(OUTPUT_DIR, f"{article_hash}.json.gz")
    with gzip.open(file_name, "wt", encoding="utf-8", compresslevel=1) as f:
        json.dump(article, f, ensure_ascii=False, separators=(',', ':'))
    
    existing_hashes.add(article_hash)

print(f"Done! Chuyển {len(existing_hashes)} bài viết sang JSON nén tại '{OUTPUT_DIR}'")
