"""
tools.py — CÁC CẢM BIẾN (SENSORS) của tác tử: nhìn vào "thế giới" Internet.

ĐÃ CUNG CẤP SẴN. Sinh viên chỉ cần DÙNG hai hàm:
    - web_search(query)      -> danh sách kết quả [{title, url, snippet}]
    - fetch_page_text(url)   -> nội dung văn bản của một trang web

Cơ chế (thứ tự ưu tiên):
    1. Tavily (TAVILY_API_KEY) — tối ưu cho AI agent, có free tier.
    2. DuckDuckGo             — miễn phí, không cần khóa API.
"""
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


def _search_tavily(query, max_results):
    """Tìm kiếm qua Tavily AI Search API (https://app.tavily.com)."""
    payload = {
        "api_key": config.TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }
    resp = requests.post("https://api.tavily.com/search", json=payload, timeout=20)
    resp.raise_for_status()
    out = []
    for r in resp.json().get("results", [])[:max_results]:
        out.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
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
        if config.TAVILY_API_KEY:
            return _search_tavily(query, max_results)
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
