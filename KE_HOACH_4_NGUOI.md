# Kế hoạch hoàn thành Lab 13 — 4 người

## Mục tiêu hoàn tất

- `python -m pytest -q` xanh; `python scripts/validate_logs.py` đạt `100/100`.
- Có ít nhất 10 trace Langfuse, gồm hai prompt version (`baseline`, `candidate`) và bằng chứng rollback `production`.
- Dashboard theo đúng sáu panel của `config/dashboard.yaml`, SLO/alert/runbook hoàn chỉnh.
- Điều tra được challenge chính thức bằng chuỗi **Metrics → Trace → Log → Root cause**.
- Hoàn thiện `submission/REPORT.md` và `submission/evidence/`; không commit `.env`, PII thô, `.venv/` hay sửa `config/challenge.json`.

## Quy ước làm việc chung

1. Một người tạo fork GitHub và mời ba người còn lại làm collaborator. Mỗi người làm trên branch riêng, ví dụ `feat/logging-pii`; chỉ merge sau khi test xanh.
2. Cả nhóm dùng cùng một project Langfuse. Chia sẻ key qua kênh bảo mật, chỉ điền vào `.env` cục bộ, tuyệt đối không gửi vào Git/chat/report.
3. Mọi evidence phải không chứa email, điện thoại, CCCD, thẻ hoặc key. Lưu ảnh/log đã che trong `submission/evidence/` và ghi đường dẫn tương đối vào report.
4. Không sửa `config/challenge.json`. File trong repo hiện đã được release; chỉ dùng script để bật/tắt incident.

## Phân vai và đầu ra

| Người | Vai trò | Phạm vi sửa chính | Bàn giao bắt buộc |
|---|---|---|---|
| 1 | Logging & PII | `app/middleware.py`, `app/main.py`, `app/logging_config.py`, có thể `app/pii.py` | Log JSON đầy đủ context, PII redact, validator 100/100, evidence log |
| 2 | Tracing & Prompt Version | Langfuse UI, `.env` cục bộ, kiểm tra `app/prompt_management.py`, `app/agent.py` | ≥10 traces, 2 prompt version, trace IDs, waterfall, ảnh rollback |
| 3 | Dashboard, SLO & Alerts | `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`, dựng dashboard | Dashboard 6 panel, ảnh runtime, validator 6/6, SLO/alert/runbook |
| 4 | Incident, Report & Integration | challenge, `submission/REPORT.md`, evidence index, test/review cuối | Báo cáo điều tra có metric/trace/log; report hoàn chỉnh; kiểm tra trước nộp |

## Tiến độ hiện tại và việc tiếp theo theo từng người

> Đánh giá dựa trên trạng thái repo sau lần pull gần nhất. Các kết quả runtime như trace Langfuse và `validate_logs.py` vẫn cần chạy lại để xác minh bằng evidence mới.

### Người 1 — Logging & PII

**Đã có trong repo**

- `app/middleware.py` đã gọi `clear_contextvars()`, nhận/generate correlation ID dạng `req-<8 hex>`, bind vào structlog và trả `x-request-id`, `x-response-time-ms`.
- `app/main.py` đã bind `user_id_hash`, `session_id`, `feature`, `model`, `env` trước event `request_received`.
- `app/logging_config.py` đã bật `scrub_event`; `app/pii.py` đã có email, phone VN, CCCD, credit card, passport và keyword địa chỉ.

**Còn phải làm**

1. Khởi động API, xóa **log runtime cũ tại máy cá nhân** nếu cần, chạy `python scripts/load_test.py` để sinh log mới.
2. Chạy `python scripts/validate_logs.py`; mục tiêu là `100/100` và không có PII leak.
3. Gửi request chứa email, phone, CCCD/thẻ để kiểm tra trực tiếp redaction; chụp/lưu một log đã che tại `submission/evidence/`.
4. Xóa các comment `TODO` đã hoàn thành để source dễ review (không bắt buộc validator, nhưng nên làm).

**Trạng thái:** Code gần hoàn thành; chưa có kết quả validator/log evidence mới để xác minh.  
**Tiêu chí bàn giao:** `validate_logs.py` 100/100 + ảnh/text evidence log correlation ID và PII redaction.

### Người 2 — Tracing & Prompt Version

**Đã có trong repo**

- Có Langfuse adapter, fallback prompt và trace generation trong `app/agent.py`.
- `app/mock_rag.py` đã có span `retrieve`; có ảnh `trace_list.png` và `trace_waterfall.png`.
- Đã có 22 traces được khai trong report, nhưng cần xác nhận trên Langfuse bằng key/project thật.

**Còn phải làm — ưu tiên cao nhất**

1. Sửa `app/agent.py`: `update_current_trace(... metadata=...)` phải gửi đúng bốn field `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`. Hiện test thất bại vì metadata chỉ có `correlation_id`.
2. Chạy `python -m pytest -q`; mục tiêu là toàn bộ test xanh (hiện: 21 pass, 1 fail).
3. Điền `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` thật trong `.env`, restart API; không commit file này.
4. Trên Langfuse tạo prompt `day13-chat`: v1 gắn `baseline` + `production`; v2 gắn `candidate`. Chạy cùng input với hai label; đổi `production` sang v2 rồi rollback v1.
5. Lưu evidence: ảnh hai version, hai trace ID thật có metadata/label/version, một waterfall và ảnh đổi label/rollback.

**Trạng thái:** Trace cơ bản có, nhưng prompt-trace contract đang lỗi và evidence version/rollback thiếu.  
**Tiêu chí bàn giao:** test xanh; ≥10 trace thật; metadata prompt đúng; evidence v1/v2/rollback đầy đủ.

### Người 3 — Dashboard, SLO & Alerts

**Đã có trong repo**

- Có `dashboard.py` (Streamlit), cấu hình dashboard và ảnh baseline/incident.
- `python scripts/validate_dashboard.py` đã pass `HỢP LỆ: 6/6 panel`.
- `config/slo.yaml`, `config/alert_rules.yaml` và `docs/alerts.md` đã được điền; có alert latency, error rate và cost.

**Còn phải làm**

1. Sau khi Người 1 tạo log mới, chạy dashboard để xác minh sáu panel lấy được dữ liệu runtime từ `data/logs.jsonl`.
2. Chụp lại dashboard có tên panel, time range 60 phút, đơn vị và threshold/SLO line rõ ràng.
3. Bật practice/official incident `rag_slow`, chạy tải, chụp panel latency tăng và tắt incident sau khi thu thập evidence.
4. Rà lại tính nhất quán: dashboard contract đặt P95 ≤ 3000 ms, còn SLO nhóm là ≤ 2000 ms; report phải giải thích 2000 ms là SLO nội bộ chặt hơn contract, hoặc thống nhất lại nếu giảng viên yêu cầu.

**Trạng thái:** Phần dashboard/config gần hoàn thành; cần runtime verification và diễn giải SLO nhất quán.  
**Tiêu chí bàn giao:** validator 6/6 + ảnh dashboard runtime baseline/incident hợp lệ + SLO/alert/runbook có thể demo.

### Người 4 — Incident, Report & Integration

**Đã có trong repo**

- `submission/REPORT.md` đã có phần phân tích challenge `day13-k3-observability-v1` / `rag_slow`.
- Root cause nêu đúng hướng: span `retrieve()` bị `time.sleep(2.5)` khi incident được bật.
- Có ảnh dashboard incident và trace waterfall.

**Còn phải làm**

1. Chạy lại challenge sau khi logging/tracing đã sửa:

   ```bash
   python scripts/inject_incident.py
   python scripts/load_test.py --challenge --concurrency 5
   ```

2. Ghi evidence kiểm chứng: metric P95, trace ID Langfuse thật, `correlation_id` và log `response_sent`/`request_failed` liên quan. Không dùng placeholder như `trace-baseline-v1`.
3. Bổ sung các evidence đang thiếu: kết quả `validate_logs.py`, PII redaction, prompt versions và rollback.
4. Sửa `REPORT.md`: thay commit SHA cuối bằng SHA của `HEAD` khi chuẩn bị nộp; hiện report ghi `a4774c4`, trong khi repo đã có commit mới hơn. Cập nhật trace IDs và đường dẫn evidence thật.
5. Kiểm tra cuối: `python -m pytest -q`, hai validator, `git status --short`; rà `.env`, `.venv`, log PII trước commit/push.

**Trạng thái:** Có khung báo cáo và phân tích đúng; evidence chưa đủ, một số ID/SHA chưa khớp repo.  
**Tiêu chí bàn giao:** Report chỉ chứa số liệu/ID/evidence xác minh được và tất cả kiểm tra cuối đều pass.

## Trình tự 4 giờ

### 0:00–0:30 — Cả nhóm: setup và baseline

- Tạo/activate `.venv`, cài `requirements.txt`, copy `.env.example` thành `.env`, điền Langfuse key.
- Terminal 1: `uvicorn app.main:app --reload --env-file .env`.
- Terminal 2: `python scripts/load_test.py`; lưu baseline `python scripts/validate_logs.py` vào evidence/report.
- Chạy `python -m pytest -q`. Nếu thiếu package, sửa môi trường trước khi sửa code.

**Mốc bàn giao:** Có `data/logs.jsonl`, baseline và server chạy được. Không cần commit log runtime.

### 0:30–1:30 — Người 1: logging và PII

1. Trong middleware: `clear_contextvars()` đầu request; nhận `x-request-id` hoặc sinh `req-<8 ký tự hex>`; `bind_contextvars(correlation_id=...)`; gắn hai response header.
2. Trong endpoint `/chat`: bind `user_id_hash`, `session_id`, `feature`, `model`, `env` **trước** log `request_received`.
3. Bật `scrub_event` trong structlog processors trước `JsonlFileProcessor`/JSON renderer. Đảm bảo scrub toàn bộ chuỗi trong payload; bổ sung pattern PII nếu phát hiện rò rỉ.
4. Xóa log cũ cục bộ (`data/logs.jsonl`), restart server, chạy load test rồi validator. Không xóa log để che lỗi; chỉ làm sạch dữ liệu baseline để validator đánh giá code mới.

**Acceptance:** log `request_received` và `response_sent` cùng correlation ID; có enrichment; PII test bị thay bằng `[REDACTED_…]`; validator 100/100.

### 1:00–2:15 — Người 2: trace và prompt version

1. Tạo text prompt `day13-chat` trên Langfuse, giữ đúng biến `feature`, `docs`, `message`.
2. Tạo v1, gắn `baseline` và `production`; tạo v2 thay đổi nhỏ, gắn `candidate`.
3. Chạy cùng input với `LANGFUSE_PROMPT_LABEL=baseline` rồi `candidate`; restart API sau mỗi lần đổi `.env` và chụp trace ID/metadata `prompt_name`, `prompt_label`, `prompt_version`.
4. Chuyển label `production` sang v2, gửi một request, sau đó rollback về v1 và chụp trước/sau.
5. Bảo đảm có ≥10 trace có metadata; chọn một trace waterfall đầy đủ.

**Acceptance:** trace phải hiển thị `prompt_source=langfuse`; không dùng `local`/`local-fallback` làm bằng chứng prompt managed.

### 1:15–2:30 — Người 3: dashboard, SLO và alert

1. Giữ nguyên contract `config/dashboard.yaml`; chạy `python scripts/validate_dashboard.py`.
2. Dựng dashboard từ `data/logs.jsonl`, gồm chính xác: latency P50/P95/P99, traffic, error/breakdown, cost, input/output tokens, quality. Hiển thị time range 60 phút, refresh 15–30 giây, đơn vị và threshold.
3. Điền SLO trong `config/slo.yaml` với lý do ngắn, nhất quán threshold: latency P95 3000 ms, error 2%, daily cost $2.5, quality 0.75.
4. Thay ba TODO trong `config/alert_rules.yaml` và ba runbook trong `docs/alerts.md`. Alert phải symptom-based, ví dụ latency P95, error rate, quality/cost; mỗi alert nêu cửa sổ thời gian, severity, owner, 3 bước kiểm tra, mitigation.
5. Chạy baseline và practice `rag_slow` để chụp panel latency thay đổi.

**Acceptance:** Validator `6/6`; screenshot nhìn rõ tên sáu panel, threshold, đơn vị, khoảng thời gian.

### 2:30–3:30 — Người 4: challenge và evidence

1. Chỉ sau khi thay đổi logging của Người 1 đã merge, đảm bảo API đang chạy rồi chạy:

   ```bash
   python scripts/inject_incident.py
   python scripts/load_test.py --challenge --concurrency 5
   ```

2. Dùng dashboard/`GET /metrics` để nêu triệu chứng. Challenge hiện tại là `day13-k3-observability-v1`, `rag_slow`, ngưỡng 2000 ms.
3. Mở một trace chậm trong Langfuse; lấy trace ID và span bất thường. Tìm log cùng `correlation_id` để chứng minh.
4. Đối chiếu code: `app/mock_rag.retrieve()` sleep 2.5 giây khi `STATE["rag_slow"]` bật. Ghi rõ đây là root cause; đề xuất mitigation (tắt/bypass RAG, timeout/fallback) và phòng ngừa (span RAG riêng, alert P95, circuit breaker/timeout).
5. Lưu ảnh metrics/dashboard, waterfall và log liên quan. Điền phần 6 report bằng ID thực, không bịa ID.

**Acceptance:** Không chỉ có kết luận; report có một metric, trace ID và correlation ID/log line có thể kiểm chứng.

### 3:30–4:00 — Cả nhóm: tích hợp và nộp

- Merge branch, chạy `python -m pytest -q`, `python scripts/validate_logs.py`, `python scripts/validate_dashboard.py`.
- Điền toàn bộ `submission/REPORT.md`: thông tin nhóm, kết quả kỹ thuật, evidence, prompt versions, challenge và đóng góp/commit của từng người.
- Kiểm tra `git status --short`, kiểm tra `.gitignore`, rà soát log/evidence để không còn PII hay secret.
- Commit/push source, config, report và evidence hợp lệ; ghi repository URL và SHA cuối vào report/Codelabs.

## Checklist evidence tối thiểu

- [ ] Baseline và kết quả cuối `validate_logs.py`.
- [ ] Log JSON có correlation ID, metadata và PII đã redact.
- [ ] Danh sách ≥10 traces và một waterfall.
- [ ] Hai prompt version + hai trace khác label/version + ảnh rollback.
- [ ] Dashboard sáu panel + validator 6/6.
- [ ] SLO, alert rules và runbook.
- [ ] Điều tra challenge: screenshot metric, trace ID/waterfall, log/correlation ID, root cause, fix, preventive measure.
- [ ] `REPORT.md` đầy đủ và bảng commit/PR của từng thành viên.
