"""
==============================================================================
 CHƯƠNG TRÌNH TÁC TỬ  —  DEEP RESEARCH AGENT (bản rút gọn cho thực hành)
==============================================================================

Đây là "bộ não" của một Tác tử thông minh biết tự nghiên cứu trên Internet.
Tác tử hoạt động theo vòng lặp:  CẢM NHẬN → SUY NGHĨ → HÀNH ĐỘNG  (lặp lại).

Trước khi lập trình, hãy phân tích tác tử theo mô hình PEAS (xem PEAS_worksheet.md):

  P (Performance) — Báo cáo đầy đủ, chính xác, có trích dẫn nguồn; ít vòng lặp thừa.
  E (Environment) — World Wide Web: máy tìm kiếm + các trang web
                    (quan sát MỘT PHẦN, ĐỘNG, NGẪU NHIÊN, THEO CHUỖI).
  A (Actuators)   — Gửi truy vấn tìm kiếm; yêu cầu tải trang; xuất báo cáo.
  S (Sensors)     — Kết quả tìm kiếm (title/url/snippet) + nội dung trang đã tải.

NHIỆM VỤ: Hoàn thành 4 phần đánh dấu  # ====== TODO(sinh viên) ======
Hàm `analyze_source` bên dưới ĐÃ LÀM SẴN làm mẫu — hãy đọc kỹ để bắt chước.
==============================================================================
"""
import config
import llm
import tools
import prompts


# ─────────────────────────────────────────────────────────────────────────────
#  VÍ DỤ MẪU (đã hoàn thành) — SENSOR → NHẬN THỨC
#  Biến nội dung một trang web thành "ghi chú" (note) phục vụ chủ đề.
#  Đây là khuôn mẫu chung: build prompt → gọi LLM → nhận JSON → trả kết quả.
# ─────────────────────────────────────────────────────────────────────────────
def analyze_source(topic, result, page_text):
    """Tóm tắt 1 trang web thành note = {"url", "summary", "useful"}."""
    user = prompts.build_analyze_user(topic, result["title"], result["url"], page_text)
    data = llm.chat_json(prompts.ANALYZE_SYSTEM, user, max_tokens=1500)
    return {
        "url": result["url"],
        "summary": data.get("summary", ""),
        "useful": bool(data.get("useful", True)),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  ====== TODO(sinh viên) 1 — ACTUATOR: sinh truy vấn tìm kiếm ======
# ─────────────────────────────────────────────────────────────────────────────
def generate_search_queries(topic, n=None):
    """Từ CHỦ ĐỀ nghiên cứu, sinh ra một DANH SÁCH truy vấn tìm kiếm (list[str]).

    Ứng với PEAS: ACTUATOR (tác tử "hành động" bằng cách gửi truy vấn tới máy tìm kiếm).

    GỢI Ý: Bắt chước analyze_source — build prompt, gọi LLM, trả về list[str].
            Khám phá module prompts để tìm hàm và hằng số phù hợp.
    """
    n = n or config.QUERIES_PER_ROUND
    raise NotImplementedError("TODO 1: hãy hoàn thành generate_search_queries()")


# ─────────────────────────────────────────────────────────────────────────────
#  ====== TODO(sinh viên) 2 — PERFORMANCE MEASURE: phản tư/đánh giá ======
# ─────────────────────────────────────────────────────────────────────────────
def reflect(topic, notes, max_followups=None):
    """Đánh giá xem các NOTE đã đủ để trả lời chủ đề chưa.

    Ứng với PEAS: PERFORMANCE MEASURE (tự đánh giá mức độ hoàn thành nhiệm vụ).

    Trả về dict: {
        "is_sufficient":    bool,
        "knowledge_gap":    str,
        "follow_up_queries": list[str],   # truy vấn bổ sung nếu chưa đủ
    }

    GỢI Ý: Cùng mẫu với TODO 1 — build prompt từ notes, gọi LLM, chuẩn hóa kết quả.
            Dùng .get() khi đọc dict để tránh KeyError.
    """
    max_followups = max_followups or config.QUERIES_PER_ROUND
    raise NotImplementedError("TODO 2: hãy hoàn thành reflect()")


# ─────────────────────────────────────────────────────────────────────────────
#  ====== TODO(sinh viên) 3 — ACTUATOR: viết báo cáo cuối ======
# ─────────────────────────────────────────────────────────────────────────────
def write_report(topic, notes):
    """Tổng hợp các NOTE thành BÁO CÁO cuối cùng (chuỗi Markdown).

    Ứng với PEAS: ACTUATOR (tác tử "hành động" bằng cách xuất kết quả cho người dùng).

    LƯU Ý: Prompt ANSWER yêu cầu trả về VĂN BẢN (Markdown), KHÔNG phải JSON
           => dùng llm.chat(messages) chứ KHÔNG dùng llm.chat_json.

    GỢI Ý: Dùng llm.chat() (KHÔNG phải chat_json) vì kết quả là văn bản Markdown.
            Xem cách truyền messages trong llm.py để biết định dạng.
    """
    raise NotImplementedError("TODO 3: hãy hoàn thành write_report()")


# ─────────────────────────────────────────────────────────────────────────────
#  ====== TODO(sinh viên) 4 — AGENT PROGRAM: vòng lặp Cảm nhận–Suy nghĩ–Hành động
# ─────────────────────────────────────────────────────────────────────────────
def run_deep_research(topic):
    """Điều phối toàn bộ tác tử. Trả về (report: str, notes: list[dict]).

    Đây là "chương trình tác tử" — nơi PEAS được kết nối lại với nhau.

    GỢI Ý: Kết nối TODO 1-3 thành vòng lặp:
        - Sinh truy vấn → tìm kiếm & tải trang → phân tích từng trang → phản tư.
        - Nếu chưa đủ và còn vòng lặp: dùng truy vấn bổ sung từ reflect().
        - Tránh tải cùng một URL hai lần.
        - In tiến trình bằng print() để quan sát tác tử "suy nghĩ".
    """
    raise NotImplementedError("TODO 4: hãy hoàn thành run_deep_research()")
