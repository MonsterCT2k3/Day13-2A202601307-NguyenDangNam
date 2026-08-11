# Tài liệu Alert Rules & Runbook

Mỗi alert phải dựa trên triệu chứng người dùng (symptom-based) hoặc vi phạm SLO, không dựa trực tiếp vào tên implementation nội bộ.

---

## Alert 1: high_latency_p95

- **Tên:** `high_latency_p95`
- **Severity:** `warning`
- **SLI/SLO liên quan:** `latency_p95_ms` (Objective: ≤ 2000 ms, Target: 99.5%)
- **Điều kiện và thời gian duy trì:** `latency_p95 > 2000ms for 5 minutes`
- **Ảnh hưởng tới người dùng:** Người dùng phản hồi hệ thống phản ứng rất chậm, thời gian chờ trả lời vượt quá 2 giây gây giảm trải nghiệm dịch vụ và nguy cơ bị HTTP client timeout.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Metrics Dashboard):** Mở Panel *Latency percentiles* trên Dashboard để xác định xu hướng P95 bắt đầu tăng từ mốc thời gian nào và liệu P50/P99 có bị ảnh hưởng tương tự không.
  2. **Bước 2 (Langfuse Traces):** Mở giao diện Traces trên Langfuse trong khoảng thời gian bị chậm, sắp xếp theo Latency giảm dần để mở Trace Waterfall. Kiểm tra xem độ trễ phân bổ vào đâu (ví dụ: `rag_retrieval`, `llm_generation`, hay `middleware`).
  3. **Bước 3 (Correlation ID & Logs):** Trích xuất `correlation_id` từ trace bị chậm và tìm kiếm trong file `data/logs.jsonl` để kiểm tra các thông số runtime, log error hoặc incident đang inject.
- **Mitigation tạm thời:** 
  - Nếu độ trễ do RAG/VectorDB bị nghẽn (ví dụ incident `rag_slow`), tạm thời bật chế độ caching hoặc fallback sang prompt rút gọn không qua RAG.
  - Nếu do LLM provider phản hồi chậm, hạ bớt `max_tokens` hoặc chuyển sang model dự phòng có độ trễ thấp hơn.
- **Owner:** `on-call-engineer`

---

## Alert 2: elevated_error_rate

- **Tên:** `elevated_error_rate`
- **Severity:** `critical`
- **SLI/SLO liên quan:** `error_rate_pct` (Objective: ≤ 2%, Target: 99.0%)
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 5 for 3 minutes`
- **Ảnh hưởng tới người dùng:** Người dùng liên tục nhận câu trả lời lỗi (HTTP 500/503), ứng dụng không trả về kết quả AI làm gián đoạn luồng làm việc.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Dashboard Error Breakdown):** Mở Panel *Error rate and breakdown* để kiểm tra tỷ lệ lỗi hiện tại và xác định loại lỗi chính (`error_type` như `llm_timeout`, `rate_limit`, `auth_error`, `internal_server_error`).
  2. **Bước 2 (Structured Logs Filtering):** Lọc các dòng log có `event == "request_failed"` trong `data/logs.jsonl` thu thập trong 3 phút qua để đọc thông điệp lỗi chi tiết và danh sách `correlation_id` bị ảnh hưởng.
  3. **Bước 3 (External Services & Traces):** Mở Langfuse Traces tìm các trace có màu đỏ (Error Status) để kiểm tra xem lỗi xảy ra ở API Gateway, kết nối LLM Provider hay hệ thống bên thứ ba.
- **Mitigation tạm thời:**
  - Nếu gặp lỗi Rate Limit/Quota từ LLM Provider, chuyển hướng traffic sang backup API key hoặc fallback provider.
  - Nếu ứng dụng bị sập cục bộ, kích hoạt Circuit Breaker hoặc restart container/service.
- **Owner:** `on-call-engineer`

---

## Alert 3: cost_budget_exceeded

- **Tên:** `cost_budget_exceeded`
- **Severity:** `warning`
- **SLI/SLO liên quan:** `daily_cost_usd` (Objective: ≤ $2.5/ngày, Target: 100%)
- **Điều kiện và thời gian duy trì:** `daily_cost_usd > 2.5`
- **Ảnh hưởng tới người dùng:** Không ảnh hưởng trực tiếp đến trải nghiệm phản hồi, nhưng có nguy cơ vượt hạn mức ngân sách ngày, dẫn tới việc dịch vụ bị tạm dừng (service suspension) do hết credit.
- **Ba bước kiểm tra đầu tiên:**
  1. **Bước 1 (Dashboard Cost & Token Panel):** Mở Panel *Cost over time* và Panel *Input and output tokens* để xem mức độ tiêu thụ token tăng đột biến ở khung giờ nào.
  2. **Bước 2 (Token-heavy Session Search):** Lọc các request trong `data/logs.jsonl` có `tokens_out` hoặc `tokens_in` cao bất thường, xác định `session_id`, `feature` hoặc `model` đóng góp nhiều chi phí nhất.
  3. **Bước 3 (Trace Inspection):** Mở các trace tiêu tốn nhiều chi phí nhất trên Langfuse để kiểm tra nội dung prompt/completion (có bị lặp vĩnh viễn, prompt injection hoặc output quá dài hay không).
- **Mitigation tạm thời:**
  - Áp dụng cấu hình `max_tokens` ngắn hơn cho các model đắt tiền.
  - Giới hạn rate-limit theo `user_id_hash` hoặc `session_id` đối với các tài khoản đang gửi request liên tục tiêu tốn nhiều token.
- **Owner:** `team-lead`
