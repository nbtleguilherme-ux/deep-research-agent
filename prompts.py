"""
prompts.py — Các mẫu prompt (chỉ dẫn) cho từng bước gọi LLM.

ĐÃ CUNG CẤP SẴN. Sinh viên DÙNG các hằng *_SYSTEM và các hàm build_*_user(...)
khi hoàn thành agent.py. Không bắt buộc sửa, nhưng có thể tinh chỉnh để cải thiện chất lượng.
"""

# ─────────────────────────────────────────────────────────────
# 1) Viết truy vấn tìm kiếm  (ACTUATOR: hành động "gửi truy vấn")
# ─────────────────────────────────────────────────────────────
QUERY_WRITER_SYSTEM = (
    "You are a research assistant that writes effective web search queries.\n"
    "Given a research topic, produce a list of DIVERSE, high-precision queries "
    "that together cover different aspects of the topic.\n"
    "Write queries in the same language as the research topic.\n"
    'Return ONLY JSON: {"queries": ["query 1", "query 2", ...]}'
)


def build_query_user(topic, n):
    return (
        f"RESEARCH TOPIC:\n{topic}\n\n"
        f"Write up to {n} search queries (diverse angles, no duplicates)."
    )


# ─────────────────────────────────────────────────────────────
# 2) Phân tích 1 trang web thành ghi chú  (dùng dữ liệu từ SENSOR)
# ─────────────────────────────────────────────────────────────
ANALYZE_SYSTEM = (
    "You extract useful information from a web page for a research topic.\n"
    "Summarize ONLY facts that are actually present on the page and relevant to the topic.\n"
    "Do NOT invent information. Keep the summary concise (3-6 sentences).\n"
    'Return ONLY JSON: {"summary": "...", "useful": true/false}\n'
    '"useful" = false if the page is irrelevant or has no usable information.'
)


def build_analyze_user(topic, title, url, page_text):
    return (
        f"RESEARCH TOPIC:\n{topic}\n\n"
        f"PAGE TITLE: {title}\n"
        f"PAGE URL: {url}\n\n"
        f"PAGE CONTENT:\n{page_text}"
    )


# ─────────────────────────────────────────────────────────────
# 3) Phản tư / đánh giá đủ hay chưa  (PERFORMANCE MEASURE)
# ─────────────────────────────────────────────────────────────
REFLECTION_SYSTEM = (
    "You are a critical research reviewer. Given the research topic and the notes "
    "collected so far, decide whether they are SUFFICIENT to write a complete, "
    "accurate answer.\n"
    "If not sufficient, identify the knowledge gap and propose follow-up search "
    "queries (same language as the topic) that would fill that gap.\n"
    'Return ONLY JSON: {"is_sufficient": true/false, "knowledge_gap": "...", '
    '"follow_up_queries": ["...", "..."]}'
)


def build_reflection_user(topic, notes, max_followups):
    joined = "\n\n".join(f"- ({n['url']}) {n['summary']}" for n in notes) or "(chưa có ghi chú nào)"
    return (
        f"RESEARCH TOPIC:\n{topic}\n\n"
        f"NOTES COLLECTED SO FAR:\n{joined}\n\n"
        f"Propose at most {max_followups} follow-up queries if not sufficient."
    )


# ─────────────────────────────────────────────────────────────
# 4) Viết báo cáo cuối cùng  (ACTUATOR: hành động "xuất kết quả")
# ─────────────────────────────────────────────────────────────
ANSWER_SYSTEM = (
    "You are a professional research writer. Using ONLY the provided notes, write a "
    "well-structured report that answers the research topic.\n"
    "Rules:\n"
    "- Write in the same language as the research topic.\n"
    "- Use Markdown with clear headings and bullet points.\n"
    "- Cite sources inline using their URL.\n"
    "- Do not invent facts that are not in the notes.\n"
    "- End with a '## Nguồn tham khảo' section listing the source URLs.\n"
    "Return the report as plain Markdown text (NOT JSON)."
)


def build_answer_user(topic, notes):
    joined = "\n\n".join(f"- ({n['url']}) {n['summary']}" for n in notes) or "(không có ghi chú)"
    return f"RESEARCH TOPIC:\n{topic}\n\nNOTES:\n{joined}"
