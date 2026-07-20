"""
solution/agent.py — LỜI GIẢI MẪU (dành cho giảng viên).

Bản đầy đủ 4 phần TODO. Chạy để đối chiếu:
    python main.py --solution "chủ đề nghiên cứu"

(Import các module hạ tầng ở thư mục cha: llm, tools, prompts, config —
 hoạt động khi chạy qua main.py vì thư mục session3 đã nằm trong sys.path.)
"""
import config
import llm
import tools
import prompts


def analyze_source(topic, result, page_text):
    """SENSOR → NHẬN THỨC: tóm tắt 1 trang web thành note."""
    user = prompts.build_analyze_user(topic, result["title"], result["url"], page_text)
    data = llm.chat_json(prompts.ANALYZE_SYSTEM, user, max_tokens=800)
    return {
        "url": result["url"],
        "summary": data.get("summary", ""),
        "useful": bool(data.get("useful", True)),
    }


# TODO 1 — ACTUATOR: sinh truy vấn tìm kiếm
def generate_search_queries(topic, n=None):
    n = n or config.QUERIES_PER_ROUND
    user = prompts.build_query_user(topic, n)
    data = llm.chat_json(prompts.QUERY_WRITER_SYSTEM, user)
    queries = data.get("queries", []) if isinstance(data, dict) else data
    queries = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
    return queries[:n] or [topic]  # dự phòng: nếu LLM trả rỗng, dùng chính chủ đề


# TODO 2 — PERFORMANCE MEASURE: phản tư/đánh giá
def reflect(topic, notes, max_followups=None):
    max_followups = max_followups or config.QUERIES_PER_ROUND
    if not notes:
        return {"is_sufficient": False, "knowledge_gap": "Chưa thu thập được thông tin nào.",
                "follow_up_queries": [topic]}
    user = prompts.build_reflection_user(topic, notes, max_followups)
    data = llm.chat_json(prompts.REFLECTION_SYSTEM, user)
    return {
        "is_sufficient": bool(data.get("is_sufficient", False)),
        "knowledge_gap": data.get("knowledge_gap", ""),
        "follow_up_queries": [q for q in data.get("follow_up_queries", []) if isinstance(q, str) and q.strip()][:max_followups],
    }


# TODO 3 — ACTUATOR: viết báo cáo cuối
def write_report(topic, notes):
    if not notes:
        return "Không tìm thấy đủ thông tin để viết báo cáo cho chủ đề này."
    user = prompts.build_answer_user(topic, notes)
    messages = [
        {"role": "system", "content": prompts.ANSWER_SYSTEM},
        {"role": "user", "content": user},
    ]
    return llm.chat(messages, temperature=0.3, max_tokens=2000)


# TODO 4 — AGENT PROGRAM: vòng lặp Cảm nhận–Suy nghĩ–Hành động
def run_deep_research(topic):
    queries = generate_search_queries(topic)
    print(f"[Vòng 1] Truy vấn: {queries}")

    notes = []
    seen_urls = set()

    for loop in range(config.MAX_RESEARCH_LOOPS + 1):
        for q in queries:
            print(f"  🔍 Tìm: {q}")
            for r in tools.web_search(q):
                url = r.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                text = tools.fetch_page_text(url)
                if not text:
                    continue
                note = analyze_source(topic, r, text)
                if note["useful"] and note["summary"]:
                    notes.append(note)
                    print(f"     ✓ Ghi chú từ {url}")

        verdict = reflect(topic, notes)
        print(f"[Đánh giá] Đủ? {verdict['is_sufficient']} | Thiếu: {verdict['knowledge_gap'][:80]}")

        if verdict["is_sufficient"] or loop == config.MAX_RESEARCH_LOOPS:
            break

        queries = verdict["follow_up_queries"] or [topic]
        print(f"[Vòng {loop + 2}] Truy vấn bổ sung: {queries}")

    report = write_report(topic, notes)
    return report, notes
