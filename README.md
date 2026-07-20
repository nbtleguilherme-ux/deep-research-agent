# Buổi thực hành 3 — Xây dựng Tác tử Nghiên cứu (Deep Research Agent)

> **Kết nối với lý thuyết:** Đây là một **Tác tử thông minh** thực thụ (Chương 2). Trước khi
> viết code, bạn phải **phân tích tác tử bằng mô hình PEAS** và nhận ra nó thuộc loại **Tác tử
> dựa trên mục tiêu + học/phản tư** hoạt động trong môi trường **quan sát một phần, động, tuần tự**.

Bản thực hành này được **rút gọn** từ một hệ *Deep Research Agent* self-host thực tế
(gốc dùng LangGraph + BAML + nhiều nhà cung cấp LLM). Ở đây đã **loại bỏ** LangGraph, BAML,
Chainlit, API server... để chỉ còn phần cốt lõi, dễ đọc và **chừa 4 chỗ trống cho bạn hoàn thành**.

---

## 1. Tác tử làm gì?

Cho một **chủ đề nghiên cứu**, tác tử tự động:

```
   Sinh truy vấn  →  Tìm kiếm web  →  Đọc & tóm tắt trang  →  Phản tư (đủ chưa?)
        ▲                                                          │
        └──────────────  chưa đủ: sinh truy vấn bổ sung  ◄─────────┘
                                                                   │ đủ / hết vòng
                                                                   ▼
                                                          Viết BÁO CÁO cuối
```

## 2. Phân tích PEAS (làm TRƯỚC khi code — nộp `PEAS_worksheet.md`)

| Thành phần | Của tác tử này |
|---|---|
| **P** — Hàm hiệu năng | Báo cáo đầy đủ & chính xác, có trích dẫn nguồn; đạt "đủ thông tin" với ít vòng lặp nhất |
| **E** — Môi trường | World Wide Web: máy tìm kiếm + các trang web (quan sát **một phần**, **động**, **ngẫu nhiên**, **theo chuỗi**, **liên tục**) |
| **A** — Bộ chấp hành | Gửi **truy vấn tìm kiếm**; yêu cầu **tải nội dung trang**; **xuất báo cáo** |
| **S** — Cảm biến | **Kết quả tìm kiếm** (title/url/snippet) + **nội dung trang web** đã tải về |

## 3. Cài đặt & kiểm tra môi trường

```bash
cd practice/session3
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
copy .env.example .env          # rồi mở .env điền OPENAI_BASE_URL / OPENAI_API_KEY / MODEL

python main.py --check          # kiểm tra LLM + web search hoạt động chưa
```

## 4. Nhiệm vụ — hoàn thành 4 hàm trong `agent.py`

Hàm `analyze_source()` **đã làm mẫu**. Hãy bắt chước để hoàn thành:

| # | Hàm | Vai trò PEAS | Gợi ý |
|---|---|---|---|
| 1 | `generate_search_queries()` | **Actuator** (gửi truy vấn) | `llm.chat_json` + `prompts.QUERY_WRITER_SYSTEM` |
| 2 | `reflect()` | **Performance** (đánh giá đủ/chưa) | `llm.chat_json` + `prompts.REFLECTION_SYSTEM` |
| 3 | `write_report()` | **Actuator** (xuất kết quả) | `llm.chat` (trả **văn bản**, không phải JSON) |
| 4 | `run_deep_research()` | **Chương trình tác tử** (vòng lặp) | Nối Sensor → Nhận thức → Performance → Actuator |

Chạy thử:

```bash
python main.py "Tác động của AI đến việc làm ở Việt Nam"
```

Báo cáo được lưu trong `output/`.

## 5. Các file

| File | Vai trò | Sửa? |
|---|---|---|
| `agent.py` | **Bộ não tác tử** — có 4 TODO | ✍️ **Sinh viên làm** |
| `PEAS_worksheet.md` | Phiếu phân tích PEAS | ✍️ **Sinh viên điền** |
| `llm.py` | Gọi LLM (chat / chat_json) | Cung cấp sẵn |
| `tools.py` | **Cảm biến**: web_search / fetch_page_text | Cung cấp sẵn |
| `prompts.py` | Mẫu prompt cho từng bước | Cung cấp sẵn |
| `config.py` | Đọc cấu hình từ `.env` | Cung cấp sẵn |
| `main.py` | Chạy tác tử từ dòng lệnh | Cung cấp sẵn |
| `solution/agent.py` | **Lời giải mẫu (giảng viên)** — `python main.py --solution "..."` | Tham khảo |

## 6. Thang điểm gợi ý

- **PEAS worksheet đúng bản chất** — 30%
- **4 hàm chạy đúng, tác tử ra báo cáo có trích dẫn** — 50%
- **Cải tiến** (tăng chất lượng truy vấn/phản tư, xử lý lỗi, chống trùng URL...) — 20%

## 7. Câu hỏi mở rộng (thảo luận)

1. Tác tử này là loại nào trong 5 cấu trúc chương trình tác tử? Vì sao?
2. Bước `reflect()` đóng vai trò gì — nó giống thành phần nào của **Tác tử học tập**?
3. Vì sao môi trường "quan sát một phần" buộc tác tử phải **lặp** nhiều vòng?