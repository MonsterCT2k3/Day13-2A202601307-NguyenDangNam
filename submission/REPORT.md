# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B4
- Repository URL: https://github.com/MonsterCT2k3/Day13-2A202601307-NguyenDangNam
- Commit SHA cuối: 1ebf5f6
- Thành viên và vai trò:

  | Thành viên | MSSV | Vai trò |
  |---|---|---|
  | Đậu Quốc Duy | 2A202601445 | Role 1 — Logging & PII |
  | Tống Nguyễn Minh Khang | 2A202601101 | Role 2 — Tracing & Prompt Version |
  | Nguyễn Hữu Tuyền | 2A202601605 | Role 3 — Dashboard, SLO & Alerts |
  | Nguyễn Đăng Nam | 2A202601307 | Role 4 — Incident, Report & Integration |

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Đạt toàn bộ tiêu chí schema, correlation ID propagation, log enrichment và PII scrubbing)
- Tổng số traces: ≥100 traces (xác minh qua Langfuse API tại thời điểm nộp, luôn ≥10 theo yêu cầu tối thiểu)
- Số PII leak còn lại: 0 (Đã kiểm tra và lọc sạch Email, Phone VN, CCCD, Credit Card)
- Link/đường dẫn dashboard: `dashboard.py` (Streamlit Dashboard)

## 3. Logging và tracing

- Evidence correlation ID: Ảnh `submission/evidence/trace_waterfall.png` có correlation ID là `req-d5107deb` ứng với log.
- Evidence PII redaction: Ảnh `submission/evidence/trace_redact_pii1.png` và `submission/evidence/trace_redact_pii2.png` trong metadata log thì số thẻ ngân hàng được redact thành [REDACTED_CREDIT_CARD].
- Evidence trace waterfall: Ảnh `submission/evidence/trace_list.png` danh sách các trace đã log (>=10 traces)
- Giải thích một span đáng chú ý: Span `GENERATION` tên `run` (ID: `96c26f27117d4c80`, Depth 1). Đây là span trung tâm bao bọc toàn bộ luồng RAG + LLM Generation, trong span metadata có kiểm soát Prompt Fallback State: Metadata hiển thị `prompt_source: "local-fallback"` và `prompt_fetch_error: "LangfuseFallback"`, chứng minh cơ chế an toàn của ứng dụng đã tự động dùng prompt cục bộ `local-v1` khi kết nối Langfuse Managed Prompt gặp sự cố.

## 4. Prompt versioning

- Prompt name: Các ảnh `submission/evidence/prompt_list.png` và `submission/evidence/prompt_list2.png` chứa các prompt baseline và candidate.
- Version/label baseline: version 1, trace trong các ảnh `submission/evidence/trace_prompt_baseline.png` và `submission/evidence/trace_prompt_baseline2.png`
- Version/label candidate: version 2, trace trong các ảnh `submission/evidence/trace_prompt_candidate.png` và `submission/evidence/trace_prompt_candidate2.png`
- Trace ID của mỗi version: `e412c5a391afe5fd25d6aeb7b3b5823f` cho baseline, `fcaa0d0d30431255a1c0b3c853f16a76` cho candidate.
- Bằng chứng đổi label hoặc rollback: Các ảnh `submission/evidence/trace_prompt_production.png` và `submission/evidence/trace_prompt_production2.png` là trace của production khi rollback về v1. Các ảnh `submission/evidence/trace_prompt_production_to_v2_1.png` và `submission/evidence/trace_prompt_production_to_v2_2.png` là trace của production prompt khi chuyển sang version 2.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard_baseline1.png` và `submission/evidence/dashboard_baseline2.png` trước incident, `submission/evidence/dashboard_incident_rag_slow1.png` và `submission/evidence/dashboard_incident_rag_slow2.png` dashboard sau khi gặp sự cố (P95 tăng từ 1369.6 ms lên 3657.2 ms, vượt ngưỡng dashboard contract và hiện `[ALERT / THRESHOLD BREACH]`).
- SLO đã chọn và lý do:
  - `latency_p95_ms` (Objective: ≤ 2000 ms, Target: 99.5%): Đảm bảo trải nghiệm phản hồi nhanh cho người dùng, tránh timeout client.
  - `error_rate_pct` (Objective: ≤ 2%, Target: 99.0%): Đảm bảo tính sẵn sàng và độ tin cậy của ứng dụng AI.
  - `daily_cost_usd` (Objective: ≤ $2.5, Target: 100.0%): Kiểm soát ngân sách API LLM không bị vượt mức cho phép.
  - `quality_score_avg` (Objective: ≥ 0.75, Target: 95.0%): Đảm bảo chất lượng câu trả lời AI đạt tiêu chuẩn nghiệp vụ.
- Lưu ý chênh lệch ngưỡng latency: `config/dashboard.yaml` (dashboard contract, không sửa) đặt vạch cảnh báo hiển thị ở P95 ≤ 3000 ms, trong khi `config/slo.yaml` và `config/alert_rules.yaml` của nhóm áp SLO nội bộ chặt hơn là P95 ≤ 2000 ms. Đây là chủ đích: dashboard giữ nguyên ngưỡng contract gốc để không phá hợp đồng chấm điểm, còn alert/SLO dùng ngưỡng nghiêm ngặt hơn để cảnh báo sớm trước khi chạm ngưỡng contract.
- Alert rules và runbook: Đã cấu hình tại `config/alert_rules.yaml` và hoàn thiện tài liệu hướng dẫn xử lý tại `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`, chạy chính thức bằng `python scripts/inject_incident.py` + `python scripts/load_test.py --challenge --concurrency 5` sau khi logging/tracing đã sửa.
- Triệu chứng từ metrics: Ngay sau khi chạy, `GET /metrics` ghi nhận `latency_p50=2651ms`, `latency_p95=4580ms` cho feature `refund` (vượt SLO 2000ms và ngưỡng dashboard 3000ms).
- **Phát hiện quan trọng — độ trễ người dùng thực tế còn nghiêm trọng hơn số liệu nội bộ:** độ trễ đo phía client (`load_test.py`, round-trip thật) của cả 5 request lên tới **~15.234s mỗi request**, cao gấp ~3.3 lần P95 mà app tự đo (4.58s). Nguyên nhân: `POST /chat` là `async def` nhưng gọi trực tiếp `agent.run()` (đồng bộ) chứa `time.sleep(2.5)` trong `retrieve()` — lệnh block này chiếm giữ toàn bộ event loop của Uvicorn (1 tiến trình, không threadpool), khiến 5 request bị xử lý tuần tự thay vì song song. Bằng chứng trong log: `request_received` của session `k3-challenge-s04` lúc `05:43:25.806846Z` gần như trùng khớp tuyệt đối với `response_sent` của session `k3-challenge-s02` lúc `05:43:25.806011Z` — tức s04 chỉ bắt đầu được xử lý ngay khi s02 vừa xong, không hề chạy song song. Vì `latency_ms` trong log/metrics/dashboard được đo bắt đầu **sau khi** request đã được dequeue, con số P95 hiện tại của dashboard **không phản ánh đúng** mức độ nghiêm trọng mà người dùng thật sự trải nghiệm khi có tải đồng thời trong lúc incident.
- Trace ID Langfuse thật, đối chiếu với `correlation_id` và log (đã verify qua Langfuse API và `data/logs.jsonl`):
  - Trace `f67c05145d273d6a2ee0ae01734b1f2a` ↔ `correlation_id=req-0db9c22c` ↔ log `response_sent` `latency_ms=4580` (session `k3-challenge-s02`)
  - Trace `e17fb297ee0d22cfb6403a5f95b5a224` ↔ `correlation_id=req-47a1dac2` ↔ log `response_sent` `latency_ms=2651` (session `k3-challenge-s04`)
  - Trace `1a000b3d4227d53a271ca3de89d1a13a` ↔ `correlation_id=req-9ac394e8` ↔ log `response_sent` `latency_ms=2651` (session `k3-challenge-s05`)
- Root cause (2 tầng):
  1. Trực tiếp: incident `rag_slow` bật `time.sleep(2.5)` trong `retrieve()` (`app/mock_rag.py`) mỗi khi tra cứu tri thức cho feature `refund`.
  2. Khuếch đại (mới phát hiện khi chạy đúng lệnh `--concurrency 5`): `retrieve()`/`resolve_prompt()` chạy đồng bộ bên trong route `async def`, chặn event loop, biến độ trễ 2.5s/request thành hiệu ứng cộng dồn theo hàng đợi cho toàn bộ traffic đồng thời.
- Fix action: Tắt incident `rag_slow` bằng `/incidents/rag_slow/disable` (đã tắt sau khi thu thập evidence). Về lâu dài: bọc `retrieve()` và `resolve_prompt()` qua `run_in_threadpool`/`asyncio.to_thread` (hoặc chuyển sang các API bất đồng bộ) để một request chậm không chặn toàn bộ throughput.
- Preventive measure: Đặt timeout cứng cho RAG span (max 1000ms), áp dụng circuit breaker và trả fallback khi retrieval quá thời gian cho phép; đồng thời bổ sung metric đo riêng thời gian xếp hàng (queue wait time) tách biệt với thời gian xử lý, để dashboard phản ánh đúng trải nghiệm người dùng dưới tải đồng thời.

## 7. Đóng góp cá nhân

| Thành viên | Vai trò | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|---|
| Đậu Quốc Duy | Role 1 — Logging & PII | Cấu hình structlog JSON, correlation ID propagation qua middleware, log enrichment và PII redaction (`app/middleware.py`, `app/main.py`, `app/logging_config.py`, `app/pii.py`); đạt `validate_logs.py` 100/100 | `f6ad75a`, `1896fad`, `a4774c4` | Thành thạo structured logging, context propagation bằng correlation ID và kỹ thuật scrub PII trước khi ghi log. |
| Tống Nguyễn Minh Khang | Role 2 — Tracing & Prompt Version | Tích hợp Langfuse tracing, gắn metadata prompt (`prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`) vào trace, quản lý prompt version baseline/candidate và rollback (`app/agent.py`, `app/prompt_management.py`) | `ac2f469`, `f11c3ec`, `12b716f` | Nắm được distributed tracing, span waterfall và quy trình prompt versioning/rollback trên Langfuse. |
| Nguyễn Hữu Tuyền | Role 3 — Dashboard, SLO & Alerts | Dựng dashboard 6 panel (Streamlit), định nghĩa SLO, alert rules và runbook (`dashboard.py`, `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`); đạt `validate_dashboard.py` 6/6 | `c433ee3`, `5ef6b17`, `6a05639` | Thiết kế dashboard observability, định nghĩa SLO/SLI và viết alert symptom-based kèm runbook xử lý sự cố. |
| Nguyễn Đăng Nam | Role 4 — Incident, Report & Integration | Điều tra challenge `rag_slow` theo chuỗi Metrics → Trace → Log → Root cause, sửa lỗi `correlation_id` bị mất khỏi Langfuse trace, tổng hợp evidence, hoàn thiện `submission/REPORT.md` và tích hợp/kiểm tra cuối trước khi nộp | `3c4317e`, `6a18bb1`, `a236af3`, `422bbcf` | Khoanh vùng root cause bằng correlation ID & trace waterfall, tích hợp 3 trụ cột Observability (Metrics, Traces, Logs) thành báo cáo điều tra hoàn chỉnh, xử lý merge/reconcile công việc nhiều thành viên. |

