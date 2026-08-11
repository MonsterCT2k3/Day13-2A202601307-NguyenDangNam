# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: MonsterCT2k3
- Repository URL: https://github.com/MonsterCT2k3/Day13-2A202601307-NguyenDangNam
- Commit SHA cuối: f11c3ec
- Thành viên và vai trò: Nguyễn Đăng Nam (Observability Engineer / Fullstack Dev)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Đạt toàn bộ tiêu chí schema, correlation ID propagation, log enrichment và PII scrubbing)
- Tổng số traces: 22 traces
- Số PII leak còn lại: 0 (Đã kiểm tra và lọc sạch Email, Phone VN, CCCD, Credit Card)
- Link/đường dẫn dashboard: `dashboard.py` (Streamlit Dashboard)

## 3. Logging và tracing

- Evidence correlation ID: `req-09355da6`, `req-4d436cfd`
- Evidence PII redaction: Các chuỗi nhạy cảm được thay thế bằng `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_CARD]` trong log
- Evidence trace waterfall: `submission/evidence/trace_waterfall.png`
- Giải thích một span đáng chú ý: Span `retrieve` trong `app/mock_rag.py` thực hiện RAG vector lookup. Khi xảy ra incident `rag_slow`, span này bị delay 2500ms, trở thành nút thắt cổ chai (bottleneck) chiếm >90% tổng latency của request (2516.4ms).

## 4. Prompt versioning

- Prompt name: `refund_assistant`
- Version/label baseline: `v1` (`production`)
- Version/label candidate: `v2` (`staging`)
- Trace ID của mỗi version: `trace-baseline-v1` và `trace-candidate-v2`
- Bằng chứng đổi label hoặc rollback: Langfuse trace metadata gắn nhãn `prompt_name: refund_assistant`, `prompt_version: 2`, `prompt_label: production`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard_baseline1.png` và `submission/evidence/dashboard_baseline2.png`
- SLO đã chọn và lý do:
  - `latency_p95_ms` (Objective: ≤ 2000 ms, Target: 99.5%): Đảm bảo trải nghiệm phản hồi nhanh cho người dùng, tránh timeout client.
  - `error_rate_pct` (Objective: ≤ 2%, Target: 99.0%): Đảm bảo tính sẵn sàng và độ tin cậy của ứng dụng AI.
  - `daily_cost_usd` (Objective: ≤ $2.5, Target: 100.0%): Kiểm soát ngân sách API LLM không bị vượt mức cho phép.
  - `quality_score_avg` (Objective: ≥ 0.75, Target: 95.0%): Đảm bảo chất lượng câu trả lời AI đạt tiêu chuẩn nghiệp vụ.
- Alert rules và runbook: Đã cấu hình tại `config/alert_rules.yaml` và hoàn thiện tài liệu hướng dẫn xử lý tại `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: P95 Latency của feature `refund` tăng đột biến từ ~150ms lên 2516.4ms (vượt quá ngưỡng SLO 2000ms), kích hoạt cảnh báo `HighP95Latency`.
- Trace ID liên quan: `req-09355da6`, `req-4d436cfd`, `req-edef54e1`
- Log line/correlation ID liên quan: `req-4d436cfd` với `event="response_sent"`, `service="api"`, `latency_ms=2516.4`
- Root cause: Incident `rag_slow` làm cho hàm `retrieve()` trong `app/mock_rag.py` thực hiện `time.sleep(2.5)` mỗi khi tra cứu tri thức liên quan tới feature `refund`.
- Fix action: Tắt incident `rag_slow` bằng `/incidents/rag_slow/disable` (trong hệ thống sản xuất: tối ưu chỉ mục vector database, thêm cache kết quả RAG).
- Preventive measure: Đặt timeout cứng cho RAG span (max 1000ms), áp dụng circuit breaker và trả về fallback response khi retrieval quá thời gian cho phép.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Đăng Nam | Xây dựng PII Redaction, Dashboard Streamlit, SLO & Alert rules, Điều tra Incident RAG Slow | `f11c3ec`, `7a57bfb`, `f1a02e5` | Thành thạo 3 trụ cột Observability (Metrics, Traces, Logs), thiết lập SLO/Alerts và kỹ năng khoanh vùng root cause bằng correlation ID & trace waterfall. |

