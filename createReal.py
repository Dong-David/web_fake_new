import os, glob, json, time, gzip
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from tqdm import tqdm

HEADERS = {"User-Agent": "Mozilla/5.0"}
DELAY = 1
SAVE_DIR = "Real"
os.makedirs(SAVE_DIR, exist_ok=True)

MAX_MB = 400

SOURCES = [
    {
        "name": "vnexpress",
        "base_url": "https://vnexpress.net",
        "category": "thoi-su",
        "link_selector": "h3.title-news a[href]",
        "title_selector": "h1.title-detail",
        "body_selector": "article.fck_detail p"
    },
    {
        "name": "vietnamnet",
        "base_url": "https://vietnamnet.vn",
        "category": "thoi-su",
        "link_selector": "h3.title a[href]",
        "title_selector": "h1.title",
        "body_selector": "div.fck_detail p"
    },
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

def folder_size_mb(folder):
    total = 0
    for f in glob.glob(os.path.join(folder, "*.json.gz")):
        total += os.path.getsize(f)
    return total / (1024*1024)

existing_files = glob.glob(os.path.join(SAVE_DIR, "*.json.gz"))
existing_hashes = set()
for f in existing_files:
    try:
        with gzip.open(f, "rt", encoding="utf-8") as file:
            data = json.load(file)
            existing_hashes.add(hash(data.get("title","") + data.get("text","")))
    except:
        continue

def get_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def get_article_links(base_url, page_url, link_selector):
    html = get_html(page_url)
    if not html: return []
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
    global existing_hashes
    if folder_size_mb(SAVE_DIR) >= MAX_MB:
        print(f"Reached {MAX_MB} MB limit. Stopping crawl.")
        exit()

    html = get_html(url)
    if not html or not is_allowed(url, source_name):
        return

    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one(title_selector)
    title = title.get_text(strip=True) if title else ""
    body = " ".join([p.get_text(strip=True) for p in soup.select(body_selector)])
    if len(body) < 50:
        return

    article_hash = hash(title + body)
    if article_hash in existing_hashes:
        return

    article = {"title": title, "text": body, "url": url, "source": source_name}
    file_name = os.path.join(SAVE_DIR, f"{article_hash}.json.gz")
    with gzip.open(file_name, "wt", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, separators=(',',':'))

    existing_hashes.add(article_hash)
    time.sleep(DELAY)

for src in SOURCES:
    base_url = src["base_url"]
    category = src["category"]
    link_selector = src["link_selector"]
    title_selector = src["title_selector"]
    body_selector = src["body_selector"]

    for year in range(2023, 2026):
        for month in range(1, 13):
            page = 1
            while True:
                page_url = f"{base_url}/{category}-p{page}"
                links = get_article_links(base_url, page_url, link_selector)
                if not links:
                    break
                for link in links:
                    save_article(link, title_selector, body_selector, src["name"])
                page += 1

print(f"Done. Total articles: {len(existing_hashes)}, Total size: {folder_size_mb(SAVE_DIR):.2f} MB")
