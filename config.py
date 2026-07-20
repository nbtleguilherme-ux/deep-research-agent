"""
config.py — Cấu hình tập trung (đọc từ file .env).

ĐÃ CUNG CẤP SẴN — sinh viên không cần sửa file này.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv chưa cài -> vẫn chạy được nếu biến môi trường đã set sẵn
    pass

# ---- LLM (endpoint tương thích OpenAI: vLLM / Ollama / OpenAI / Gemini-compat...) ----
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# ---- Web search ----
# Nếu có SERPER_API_KEY (serper.dev) -> dùng Google qua Serper; nếu trống -> dùng DuckDuckGo miễn phí.
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()

# ---- Tham số nghiên cứu ----
MAX_RESEARCH_LOOPS = int(os.getenv("MAX_RESEARCH_LOOPS", "2"))   # số vòng lặp bổ sung tối đa
QUERIES_PER_ROUND = int(os.getenv("QUERIES_PER_ROUND", "3"))     # số truy vấn mỗi vòng
RESULTS_PER_QUERY = int(os.getenv("RESULTS_PER_QUERY", "4"))     # số kết quả lấy cho mỗi truy vấn
MAX_PAGE_CHARS = int(os.getenv("MAX_PAGE_CHARS", "6000"))        # cắt bớt nội dung trang để tiết kiệm token
