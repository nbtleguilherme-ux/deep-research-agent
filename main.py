"""
main.py — Chạy tác tử từ dòng lệnh.

Cách dùng:
    python main.py "chủ đề nghiên cứu của bạn"
    python main.py --check         # kiểm tra môi trường (LLM + web search) trước khi code
    python main.py --solution "chủ đề"   # chạy bản lời giải mẫu của giảng viên

ĐÃ CUNG CẤP SẴN — sinh viên không cần sửa.
"""
import sys
import os
import datetime

import config
import llm
import tools


def check_environment():
    """Kiểm tra nhanh: gọi được LLM chưa, tìm kiếm web chưa."""
    print("== KIỂM TRA MÔI TRƯỜNG ==")
    print(f"LLM   : Gemini  (model={config.GEMINI_MODEL})")
    print(f"Search: {'Tavily' if config.TAVILY_API_KEY else 'DuckDuckGo (miễn phí)'}")
    try:
        msg = llm.chat([{"role": "user", "content": "Trả lời đúng một từ: OK"}], max_tokens=10)
        print(f"[LLM ] Phản hồi: {msg.strip()[:60]}")
    except Exception as e:
        print(f"[LLM ] LỖI: {e}")
    try:
        results = tools.web_search("Trí tuệ nhân tạo là gì", max_results=2)
        print(f"[Web ] Tìm được {len(results)} kết quả. Ví dụ: {results[0]['url'] if results else '(trống)'}")
        if results:
            text = tools.fetch_page_text(results[0]["url"])
            print(f"[Fetch] Tải được {len(text)} ký tự từ trang đầu tiên.")
    except Exception as e:
        print(f"[Web ] LỖI: {e}")


def main():
    argv = sys.argv[1:]

    if "--check" in argv:
        check_environment()
        return

    use_solution = "--solution" in argv
    topic_parts = [a for a in argv if not a.startswith("--")]
    topic = " ".join(topic_parts).strip() or input("Nhập chủ đề nghiên cứu: ").strip()
    if not topic:
        print("Chưa có chủ đề. Kết thúc.")
        return

    if use_solution:
        from solution import agent  # bản lời giải của giảng viên
    else:
        import agent                # bản sinh viên hoàn thành

    print(f"\n🔎 Bắt đầu nghiên cứu: {topic}\n" + "=" * 60)
    report, notes = agent.run_deep_research(topic)

    print("\n" + "=" * 60 + "\n📄 BÁO CÁO CUỐI CÙNG\n" + "=" * 60)
    print(report)

    # Lưu kết quả
    os.makedirs("output", exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("output", f"report_{stamp}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n{report}\n")
    print(f"\n✅ Đã lưu báo cáo: {path}  (tổng {len(notes)} ghi chú)")


if __name__ == "__main__":
    main()
