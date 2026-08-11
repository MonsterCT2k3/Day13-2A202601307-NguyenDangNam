# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B4
- Repository URL: https://github.com/MonsterCT2k3/Day13-2A202601307-NguyenDangNam
- Commit SHA cuối: 1b0adbc
- Thành viên và vai trò:

  | Thành viên | MSSV | Vai trò |
  |---|---|---|
  | Đậu Quốc Duy | 2A202601445 | Role 1 — Logging & PII |
  | Tống Nguyễn Minh Khang | 2A202601101 | Role 2 — Tracing & Prompt Version |
  | Nguyễn Hữu Tuyền | 2A202601605 | Role 3 — Dashboard, SLO & Alerts |
  | Nguyễn Đăng Nam | 2A202601307 | Role 4 — Incident, Report & Integration |

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

- Prompt name: Các ảnh `submission/evidence/prompt_list.png` và `submission/evidence/prompt_list2.png` chứa các prompt baseline và candidate.
- Version/label baseline: version 1, trace trong các ảnh `submission/evidence/baseline.png` và `submission/evidence/baseline2.png`
- Version/label candidate: version 2, trace trong các ảnh `submission/evidence/candidate.png` và `submission/evidence/candidate2.png`
- Trace ID của mỗi version: `e412c5a391afe5fd25d6aeb7b3b5823f` cho baseline, `fcaa0d0d30431255a1c0b3c853f16a76` cho candidate.
- Bằng chứng đổi label hoặc rollback: Các ảnh `submission/evidence/trace_prompt_production.png` và `submission/evidence/trace_prompt_production2.png` là trace của production khi rollback về v1. Các ảnh `submission/evidence/trace_prompt_production_to_v2_1.png` và `submission/evidence/trace_prompt_production_to_v2_2.png` là trace của production prompt khi chuyển sang version 2.

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

| Thành viên | Vai trò | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|---|
| Đậu Quốc Duy | Role 1 — Logging & PII | Cấu hình structlog JSON, correlation ID propagation qua middleware, log enrichment và PII redaction (`app/middleware.py`, `app/main.py`, `app/logging_config.py`, `app/pii.py`); đạt `validate_logs.py` 100/100 | | Thành thạo structured logging, context propagation bằng correlation ID và kỹ thuật scrub PII trước khi ghi log. |
| Tống Nguyễn Minh Khang | Role 2 — Tracing & Prompt Version | Tích hợp Langfuse tracing, gắn metadata prompt (`prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`) vào trace, quản lý prompt version baseline/candidate và rollback (`app/agent.py`, `app/prompt_management.py`) | | Nắm được distributed tracing, span waterfall và quy trình prompt versioning/rollback trên Langfuse. |
| Nguyễn Hữu Tuyền | Role 3 — Dashboard, SLO & Alerts | Dựng dashboard 6 panel (Streamlit), định nghĩa SLO, alert rules và runbook (`dashboard.py`, `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`); đạt `validate_dashboard.py` 6/6 | | Thiết kế dashboard observability, định nghĩa SLO/SLI và viết alert symptom-based kèm runbook xử lý sự cố. |
| Nguyễn Đăng Nam | Role 4 — Incident, Report & Integration | Điều tra challenge `rag_slow` theo chuỗi Metrics → Trace → Log → Root cause, tổng hợp evidence, hoàn thiện `submission/REPORT.md` và kiểm tra tích hợp trước khi nộp | `f11c3ec`, `7a57bfb`, `f1a02e5` | Khoanh vùng root cause bằng correlation ID & trace waterfall, tích hợp 3 trụ cột Observability (Metrics, Traces, Logs) thành báo cáo điều tra hoàn chỉnh. |

