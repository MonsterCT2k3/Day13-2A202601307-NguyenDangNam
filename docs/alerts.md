# Tài liệu Alert Rules & Runbook Hướng dẫn Xử lý Sự cố

Tài liệu này định nghĩa các quy tắc cảnh báo (Alert Rules) dựa trên triệu chứng người dùng (symptom-based) và quy trình chuẩn (Runbook) để đội ngũ vận hành phản ứng nhanh khi xảy ra vi phạm SLO.

---

## Alert 1: high_latency_p95

- **Tên cảnh báo:** `high_latency_p95`
- **Mức độ nghiêm trọng (Severity):** `warning`
- **Chỉ số SLI/SLO liên quan:** `latency_p95_ms` (Objective: ≤ 2000 ms, Target: 99.5%)
- **Điều kiện và thời gian duy trì:** `latency_p95 > 2000ms for 5 minutes`
- **Ảnh hưởng tới người dùng:** Người dùng gặp hiện tượng phản hồi chậm trễ khi chat/tương tác với AI, thời gian chờ vượt quá 2 giây gây gián đoạn trải nghiệm và tăng nguy cơ timeout tại client/gateway.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Kiểm tra Dashboard Metrics):** Mở Panel *Latency percentiles* trên Streamlit Dashboard (`http://localhost:8501`) để xác định xu hướng P95 bắt đầu tăng từ thời điểm nào, đồng thời quan sát xem P50 và P99 có tăng đột biến theo không.
  2. **Bước 2 (Khoanh vùng qua Traces Waterfall):** Truy cập giao diện Tracing (Langfuse) trong khung thời gian xảy ra cảnh báo, sắp xếp traces theo thời gian xử lý giảm dần và mở Trace Waterfall. Kiểm tra xem độ trễ tập trung tại span nào: `mock_rag.retrieve` (RAG Vector lookup), `llm_generation` hay tầng middleware.
  3. **Bước 3 (Truy vết Logs qua Correlation ID):** Lấy `correlation_id` của các trace chậm nhất và lọc trong `data/logs.jsonl` để kiểm tra event log chi tiết, service bị ảnh hưởng hoặc các incident đang kích hoạt.
- **Biện pháp giảm thiểu tạm thời (Mitigation):**
  - Nếu độ trễ bắt nguồn từ RAG Retrieval (như incident `rag_slow`), tạm thời kích hoạt bypass/caching hoặc chuyển sang prompt trực tiếp không qua tra cứu RAG.
  - Nếu do nhà cung cấp LLM phản hồi chậm, hạ bớt tham số `max_tokens` hoặc chuyển sang model dự phòng.
- **Người phụ trách (Owner):** `on-call-engineer`

---

## Alert 2: elevated_error_rate

- **Tên cảnh báo:** `elevated_error_rate`
- **Mức độ nghiêm trọng (Severity):** `critical`
- **Chỉ số SLI/SLO liên quan:** `error_rate_pct` (Objective: ≤ 2%, Target: 99.0%)
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 2 for 3 minutes`
- **Ảnh hưởng tới người dùng:** Người dùng nhận thông báo lỗi HTTP 500/503 hoặc phản hồi rỗng từ API, tính năng chat AI bị gián đoạn hoàn toàn.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Phân tích Error Breakdown trên Dashboard):** Mở Panel *Error rate and breakdown* trên Dashboard để xác định tỷ lệ lỗi hiện tại và biểu đồ tròn phân loại lỗi theo `error_type` (`internal_error`, `llm_timeout`, `auth_error`, `rate_limit`).
  2. **Bước 2 (Lọc Structured Logs):** Lọc tất cả các bản ghi có `event == "request_failed"` trong `data/logs.jsonl` trong vòng 3–5 phút gần nhất để xem chi tiết thông báo lỗi (exception trace) và tập hợp `user_id_hash` bị ảnh hưởng.
  3. **Bước 3 (Kiểm tra Traces bị lỗi):** Tìm các trace có trạng thái lỗi (Error status) trên hệ thống Tracing để xác định lỗi xuất phát từ API Gateway, Service nội bộ hay kết nối bên ngoài.
- **Biện pháp giảm thiểu tạm thời (Mitigation):**
  - Nếu lỗi do cạn kiệt Quota / Rate Limit của LLM, lập tức trỏ sang API Key dự phòng hoặc fallback endpoint.
  - Kích hoạt Circuit Breaker để bảo vệ dịch vụ phía sau và trả về thông báo lỗi thân thiện thay vì làm sập ứng dụng.
- **Người phụ trách (Owner):** `on-call-engineer`

---

## Alert 3: cost_budget_exceeded

- **Tên cảnh báo:** `cost_budget_exceeded`
- **Mức độ nghiêm trọng (Severity):** `warning`
- **Chỉ số SLI/SLO liên quan:** `daily_cost_usd` (Objective: ≤ $2.5/ngày, Target: 100.0%)
- **Điều kiện và thời gian duy trì:** `daily_cost_usd > 2.5`
- **Ảnh hưởng tới người dùng:** Không ảnh hưởng tức thời tới độ trễ, nhưng nếu chi phí vượt ngân sách quá mức có thể dẫn đến việc tài khoản LLM bị khóa dịch vụ do hết credit.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Kiểm tra Panel Cost & Token trên Dashboard):** Quan sát Panel *Cost over time* và *Input and output tokens* để nhận diện thời điểm chi phí và token tiêu thụ tăng vọt.
  2. **Bước 2 (Lọc Session tiêu thụ nhiều Token):** Phân tích `data/logs.jsonl`, nhóm theo `session_id`, `feature` và `model` để tìm các phiên làm việc tiêu tốn token bất thường.
  3. **Bước 3 (Kiểm tra Trace nội dung Prompt/Output):** Mở trace của các session tốn kém nhất trên Langfuse để kiểm tra xem có hiện tượng lặp vô tận (infinite loop), prompt injection làm phình độ dài output hay không.
- **Biện pháp giảm thiểu tạm thời (Mitigation):**
  - Giới hạn cứng `max_tokens` cho các model cao cấp.
  - Tạm thời áp dụng Rate-Limiting chặt chẽ hơn theo `user_id_hash` đối với các user spam request.
- **Người phụ trách (Owner):** `team-lead`
