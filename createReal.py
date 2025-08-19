import os, glob, json, time, gzip, hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Mozilla/5.0"}
SAVE_DIR = "Real"
os.makedirs(SAVE_DIR, exist_ok=True)

MAX_MB = 400            
MAX_WORKERS = 8
RETRY = 3               

SOURCES = [
    {"name":"vnexpress","base_url":"https://vnexpress.net","category":"thoi-su",
     "link_selector":"h3.title-news a[href]","title_selector":"h1.title-detail",
     "body_selector":"article.fck_detail p"},
    {"name":"vietnamnet","base_url":"https://vietnamnet.vn","category":"thoi-su",
     "link_selector":"h3.title a[href]","title_selector":"h1.title",
     "body_selector":"div.fck_detail p"},
    {"name":"baochinhphu","base_url":"https://baochinhphu.vn","category":"thoi-su",
     "link_selector":"h3.news-title a[href]","title_selector":"h1.title",
     "body_selector":"div.news-content p"},
    {"name":"who","base_url":"https://www.who.int/news","category":"health",
     "link_selector":"a.link-container[href]","title_selector":"h1.headline",
     "body_selector":"div.sf-detail-body-wrapper p"},
    {"name":"bao_congan","base_url":"https://cand.com.vn","category":"thoi-su",
     "link_selector":"h3.title a[href]","title_selector":"h1.title-detail",
     "body_selector":"div.detail-content p"},
    {"name":"bo_congthuong","base_url":"https://www.moit.gov.vn","category":"thoi-su",
     "link_selector":"h3.title a[href]","title_selector":"h1.title-detail",
     "body_selector":"div.content-detail p"},
]

robots_parsers = {}
for src in SOURCES:
    rp = RobotFileParser()
    rp.set_url(urljoin(src["base_url"], "/robots.txt"))
    rp.read()
    robots_parsers[src["name"]] = rp

def is_allowed(url, source_name):
    rp = robots_parsers.get(source_name)
    return rp.can_fetch(HEADERS["User-Agent"], url) if rp else True

def current_dir_mb():
    total = 0
    for f in glob.glob(os.path.join(SAVE_DIR, "*")):
        total += os.path.getsize(f)
    return total / (1024*1024)

existing_files = glob.glob(os.path.join(SAVE_DIR, "*.json.gz"))
existing_hashes = set()
for f in existing_files:
    try:
        with gzip.open(f, "rt", encoding="utf-8") as file:
            data = json.load(file)
            existing_hashes.add(hash(data.get("title","")+data.get("text","")))
    except:
        continue

def get_html(url):
    for attempt in range(RETRY):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(1)
    return None

def get_article_links(base_url, page_url, link_selector):
    html = get_html(page_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select(link_selector):
        link = a.get("href")
        if link and not link.startswith("http"):
            link = urljoin(base_url, link)
        if link and link not in links:
            links.append(link)
    return links

def save_article(url, title_selector, body_selector, source_name):
    html = get_html(url)
    if not html or not is_allowed(url, source_name):
        return None
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one(title_selector)
    title = title.get_text(strip=True) if title else ""
    body = " ".join([p.get_text(strip=True) for p in soup.select(body_selector)])
    if len(body) < 50:
        return None
    article_hash = hash(title + body)
    if article_hash in existing_hashes:
        return None
    article = {"title": title, "text": body, "url": url, "source": source_name}
    file_name = os.path.join(SAVE_DIR, f"{article_hash}.json.gz")
    with gzip.open(file_name, "wt", encoding="utf-8", compresslevel=1) as f:
        json.dump(article, f, ensure_ascii=False, separators=(',',':'))
    existing_hashes.add(article_hash)
    return article_hash

def crawl_source(src):
    base_url = src["base_url"]
    category = src["category"]
    link_selector = src["link_selector"]
    title_selector = src["title_selector"]
    body_selector = src["body_selector"]

    for year in range(2010, 2026):
        for month in range(1, 13):
            page = 1
            while True:
                if current_dir_mb() >= MAX_MB:
                    print(f"Reached {MAX_MB} MB. Stopping crawl.")
                    return
                page_url = f"{base_url}/{category}-p{page}"
                links = get_article_links(base_url, page_url, link_selector)
                if not links:
                    break
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = [executor.submit(save_article, link, title_selector, body_selector, src["name"]) for link in links]
                    for fut in as_completed(futures):
                        if current_dir_mb() >= MAX_MB:
                            print(f"Reached {MAX_MB} MB. Stopping crawl.")
                            return
                page += 1

for src in SOURCES:
    crawl_source(src)

print(f"Done. Total articles: {len(existing_hashes)}, Size: {current_dir_mb():.2f} MB")
