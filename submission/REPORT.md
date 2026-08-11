# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: Ảnh `submission/evidence/trace_waterfall.png` có correlation ID là `req-d5107deb` ứng với log.
- Evidence PII redaction: Ảnh `submission/evidence/trace_redact_pii1.png` và `submission/evidence/trace_redact_pii2.png` trong metadata log thì số thẻ ngân hàng được redact thành [REDACTED_CREDIT_CARD].
- Evidence trace waterfall: Ảnh `submission/evidence/trace_list.png` danh sách các trace đã log (>=10 traces)
- Giải thích một span đáng chú ý: Span `GENERATION` tên `run` (ID: `96c26f27117d4c80`, Depth 1). Đây là span trung tâm bao bọc toàn bộ luồng RAG + LLM Generation với các điểm quan trọng:
  1. Đo lường thời gian & Phân rã độ trễ: Span có tổng latency ~1,017ms, chứa 2 span con bên dưới là `retrieve` (<1ms) và `generate` (~150ms).
  2. Kiểm soát Prompt Fallback State: Metadata hiển thị `prompt_source: "local-fallback"` và `prompt_fetch_error: "LangfuseFallback"`, chứng minh cơ chế an toàn của ứng dụng đã tự động dùng prompt cục bộ `local-v1` khi kết nối Langfuse Managed Prompt gặp sự cố.
  3. Truy vết Input/Output & Token Usage: Span con `generate` (ID: `72048e6319626628`) ghi nhận chính xác prompt compiled đầy đủ (`Feature=qa\nDocs=...\nQuestion=...`), câu trả lời của model `claude-sonnet-4-5` và số token tiêu thụ (27 input tokens, 111 output tokens).

## 4. Prompt versioning

- Prompt name: Các ảnh `submission/evidence/prompt_list.png` và `submission/evidence/prompt_list2.png` chứa các prompt baseline và candidate.
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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
