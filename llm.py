"""
llm.py — Bộ gọi Google Gemini qua SDK chính thức (google-genai).

ĐÃ CUNG CẤP SẴN. Sinh viên chỉ cần DÙNG hai hàm:
    - chat(messages)         -> trả về chuỗi văn bản
    - chat_json(system, user) -> trả về đối tượng Python (dict/list) từ JSON mà LLM sinh ra
"""
import json
import re
import time

from google import genai
from google.genai import types

import config

_client = genai.Client(api_key=config.GEMINI_API_KEY)


def _parse_retry_delay(error_msg, default=30):
    """Đọc thời gian chờ gợi ý từ thông báo lỗi quota (seconds: N)."""
    match = re.search(r"seconds:\s*(\d+)", error_msg)
    return int(match.group(1)) + 2 if match else default


def chat(messages, temperature=0.3, max_tokens=1500):
    """Gọi Gemini với danh sách messages theo chuẩn OpenAI Chat Completions.

    messages = [{"role": "system"/"user"/"assistant", "content": "..."}]
    Trả về: nội dung văn bản của phản hồi.
    """
    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    turns = [m for m in messages if m["role"] != "system"]

    gen_config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        system_instruction="\n".join(system_parts) if system_parts else None,
    )

    # Tất cả turns trừ tin nhắn cuối cùng -> đưa vào history
    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in turns[:-1]
    ]
    last_msg = turns[-1]["content"] if turns else ""

    for attempt in range(4):
        try:
            chat_session = _client.chats.create(
                model=config.GEMINI_MODEL,
                config=gen_config,
                history=history,
            )
            response = chat_session.send_message(last_msg)
            return response.text
        except Exception as e:
            msg = str(e)
            # Chỉ retry khi bị giới hạn tốc độ theo phút (429), không retry giới hạn ngày
            if "429" in msg and "PerDay" not in msg:
                wait = _parse_retry_delay(msg, default=30 * (2 ** attempt))
                print(f"[LLM] Rate limit, chờ {wait}s... (lần {attempt + 1}/3)")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Vượt quá số lần thử lại do rate limit.")


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
