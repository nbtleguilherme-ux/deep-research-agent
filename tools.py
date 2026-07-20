"""
tools.py — CÁC CẢM BIẾN (SENSORS) của tác tử: nhìn vào "thế giới" Internet.

ĐÃ CUNG CẤP SẴN. Sinh viên chỉ cần DÙNG hai hàm:
    - web_search(query)      -> danh sách kết quả [{title, url, snippet}]
    - fetch_page_text(url)   -> nội dung văn bản của một trang web

Cơ chế:
    * Nếu có SERPER_API_KEY  -> tìm kiếm Google qua serper.dev (chất lượng cao).
    * Nếu không              -> dùng DuckDuckGo (miễn phí, không cần khóa API).
"""
import json
import http.client

import requests

import config

try:
    import trafilatura  # trích xuất nội dung chính của trang (nếu đã cài)
except ImportError:
    trafilatura = None

from bs4 import BeautifulSoup

_UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}


def _search_serper(query, max_results):
    conn = http.client.HTTPSConnection("google.serper.dev", timeout=20)
    payload = json.dumps({"q": query})
    headers = {"X-API-KEY": config.SERPER_API_KEY, "Content-Type": "application/json"}
    conn.request("POST", "/search", payload, headers)
    data = json.loads(conn.getresponse().read().decode("utf-8"))
    out = []
    for r in data.get("organic", [])[:max_results]:
        out.append({
            "title": r.get("title", ""),
            "url": r.get("link", ""),
            "snippet": r.get("snippet", ""),
        })
    return out


def _search_ddg(query, max_results):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS  # tên gói cũ
    out = []
    with DDGS() as ddg:
        for r in ddg.text(query, max_results=max_results):
            out.append({
                "title": r.get("title", ""),
                "url": r.get("href") or r.get("url", ""),
                "snippet": r.get("body") or r.get("snippet", ""),
            })
    return out


def web_search(query, max_results=None):
    """Tìm kiếm web, trả về danh sách [{title, url, snippet}]."""
    max_results = max_results or config.RESULTS_PER_QUERY
    try:
        if config.SERPER_API_KEY:
            return _search_serper(query, max_results)
        return _search_ddg(query, max_results)
    except Exception as e:
        print(f"[web_search] Lỗi khi tìm '{query}': {e}")
        return []


def fetch_page_text(url, max_chars=None):
    """Tải một trang web và trích xuất nội dung văn bản (cắt bớt cho gọn)."""
    max_chars = max_chars or config.MAX_PAGE_CHARS
    try:
        resp = requests.get(url, headers=_UA, timeout=15, verify=False)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or resp.encoding
        html = resp.text

        text = ""
        if trafilatura is not None:
            text = trafilatura.extract(html) or ""
        if not text:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)

        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[Đã cắt bớt nội dung]"
        return text.strip()
    except Exception as e:
        print(f"[fetch_page_text] Không tải được {url}: {e}")
        return ""


# Tắt cảnh báo verify=False cho gọn log khi demo
try:
    requests.packages.urllib3.disable_warnings()  # type: ignore
except Exception:
    pass
