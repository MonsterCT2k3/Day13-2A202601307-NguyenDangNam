# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: MonsterCT2k3
- Repository URL: https://github.com/MonsterCT2k3/Day13-2A202601307-NguyenDangNam
- Commit SHA cuối: 5ef6b17
- Thành viên và vai trò: Nguyễn Đăng Nam (Observability Engineer / Fullstack Dev)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Đạt toàn bộ tiêu chí schema, correlation ID propagation, log enrichment và PII scrubbing)
- Tổng số traces: 22 traces
- Số PII leak còn lại: 0 (Đã kiểm tra và lọc sạch Email, Phone VN, CCCD, Credit Card)
- Link/đường dẫn dashboard: `dashboard.py` (Streamlit Dashboard)

## 3. Logging và tracing

- Evidence correlation ID: Ảnh `submission/evidence/trace_waterfall.png` có correlation ID là `req-d5107deb` ứng với log.
- Evidence PII redaction: Ảnh `submission/evidence/trace_redact_pii1.png` và `submission/evidence/trace_redact_pii2.png` trong metadata log thì số thẻ ngân hàng được redact thành [REDACTED_CREDIT_CARD].
- Evidence trace waterfall: Ảnh `submission/evidence/trace_list.png` danh sách các trace đã log (>=10 traces)
- Giải thích một span đáng chú ý: Span `GENERATION` tên `run` (ID: `96c26f27117d4c80`, Depth 1). Đây là span trung tâm bao bọc toàn bộ luồng RAG + LLM Generation, trong span metadata có kiểm soát Prompt Fallback State: Metadata hiển thị `prompt_source: "local-fallback"` và `prompt_fetch_error: "LangfuseFallback"`, chứng minh cơ chế an toàn của ứng dụng đã tự động dùng prompt cục bộ `local-v1` khi kết nối Langfuse Managed Prompt gặp sự cố.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard_baseline1.png` và `submission/evidence/dashboard_baseline2.png` trước incident, `submission/evidence/dashboard_incident_rag_slow_1.png` và `submission/evidence/dashboard_incident_rag_slow_2.png` dashboard sau khi gặp sự cố
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

