import json, os, random, glob, gzip

FAKE_DIR = "Fake"
REAL_DIR = "Real"
os.makedirs(FAKE_DIR, exist_ok=True)

real_files = glob.glob(os.path.join(REAL_DIR, "*.json.gz"))
num_real = len(real_files)

titles = [
    "Bão mới sắp đổ bộ miền Trung",
    "Giá xăng tăng kỷ lục, người dân lo lắng",
    "Thị trường chứng khoán hôm nay biến động mạnh",
    "Hội thảo khoa học quốc tế tại Hà Nội",
    "Công nghệ AI thay đổi ngành giáo dục"
]
descriptions = [
    "Tin tức mới cập nhật về sự kiện quan trọng hôm nay.",
    "Bản tin nhanh về tình hình kinh tế xã hội.",
    "Sự kiện nóng được nhiều người quan tâm.",
    "Thông tin chi tiết về dự án nghiên cứu mới.",
    "Những thay đổi đáng chú ý trong ngành công nghiệp."
]
bodies = [
    "Nhiều người dân đã chuẩn bị đồ dùng cần thiết để đối phó với bão.",
    "Giá xăng liên tục tăng trong tuần này khiến nhiều người phải tính toán chi tiêu.",
    "Thị trường chứng khoán hôm nay có nhiều biến động, các nhà đầu tư cần thận trọng.",
    "Hội thảo thu hút hàng trăm nhà khoa học tham dự, thảo luận về các vấn đề cấp thiết.",
    "Công nghệ AI đang được áp dụng trong giáo dục, giúp học sinh tiếp cận thông tin hiệu quả."
]

existing_hashes = set()
for f in glob.glob(os.path.join(FAKE_DIR, "*.json.gz")):
    try:
        with gzip.open(f, "rt", encoding="utf-8") as file:
            data = json.load(file)
        existing_hashes.add(hash(data.get("title","")+data.get("text","")))
    except:
        continue

i = len(existing_hashes)
while len(existing_hashes) < num_real:
    title = random.choice(titles)
    desc = random.choice(descriptions)
    body_text = " ".join(random.choices(bodies, k=random.randint(2,3)))
    
    article_hash = hash(title + body_text)
    if article_hash in existing_hashes:
        continue
    
    article = {"title": title, "description": desc, "text": body_text, "url": f"fake://article{i}"}
    file_name = os.path.join(FAKE_DIR, f"fake_{i}.json.gz")
    with gzip.open(file_name, "wt", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, separators=(',',':'))
    
    existing_hashes.add(article_hash)
    i += 1

print(f"Created {len(existing_hashes)} fake articles, balanced with real ones.")
