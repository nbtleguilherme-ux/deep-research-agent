"""
llm.py — Bộ gọi Mô hình ngôn ngữ (LLM) qua API tương thích OpenAI.

ĐÃ CUNG CẤP SẴN. Sinh viên chỉ cần DÙNG hai hàm:
    - chat(messages)      -> trả về chuỗi văn bản
    - chat_json(system, user) -> trả về đối tượng Python (dict/list) từ JSON mà LLM sinh ra
"""
import json
import re
import requests

import config


def chat(messages, temperature=0.3, max_tokens=1500):
    """Gọi LLM với danh sách messages theo chuẩn OpenAI Chat Completions.

    messages = [{"role": "system"/"user"/"assistant", "content": "..."}]
    Trả về: nội dung văn bản của phản hồi.
    """
    url = f"{config.OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def extract_json(text):
    """Trích xuất JSON từ phản hồi của LLM (chịu được ```json ... ``` và văn bản thừa)."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # Thử tìm khối JSON đầu tiên nằm cân bằng ({...} hoặc [...])
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = text.find(open_ch)
        end = text.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                continue
    raise ValueError(f"Không tìm thấy JSON hợp lệ trong phản hồi LLM:\n{text[:500]}")


def chat_json(system, user, temperature=0.2, max_tokens=1500):
    """Gọi LLM và ép phân tích kết quả thành JSON (dict/list)."""
    content = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return extract_json(content)
