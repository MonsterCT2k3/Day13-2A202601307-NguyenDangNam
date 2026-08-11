# Anomaly detection evidence — `scripts/detect_anomalies.py`

Script tự động quét `data/logs.jsonl`, phát hiện 2 loại anomaly:
1. **PII leak**: tái sử dụng `PII_PATTERNS` từ `app/pii.py`, quét toàn bộ dòng log tìm
   chuỗi khớp pattern PII mà KHÔNG nằm ngay sau marker `[REDACTED_...]` (tức là leak thật
   sự chưa được scrub, không phải false positive từ text đã che).
2. **Latency SLO violation**: đọc ngưỡng `latency_p95_ms.objective` trực tiếp từ
   `config/slo.yaml` (2000 ms), so khớp từng `response_sent.latency_ms` trong log.

## Chạy trên `data/logs.jsonl` thật của repo

```
--- Anomaly Detection Report ---
PII leaks detected: 0
Latency SLO violations (> 2000 ms, 10 request):
  [line 25] correlation_id=req-9c35768e feature=refund latency_ms=4320
  [line 27] correlation_id=req-72cc13de feature=refund latency_ms=2651
  ... (8 dòng tương tự, đều từ challenge rag_slow đã điều tra ở mục 6)

[ALERT] Phát hiện anomaly trong log.
```

→ 0 PII leak (xác nhận redaction hoạt động đúng trên toàn bộ log thật), và script bắt
đúng 10 request bị `rag_slow` làm chậm trong lần chạy challenge chính thức — khớp với
các trace/correlation_id đã dẫn chứng ở mục 6 của report.

## Self-test: xác nhận script thực sự phát hiện được leak/violation (không chỉ báo 0 mặc định)

Chạy trên 1 file log giả có 1 email chưa che và 1 latency 9999ms:

```
PII leaks detected: 1
  [line 1] pattern=email match='leak@example.com'
Latency SLO violations (> 2000 ms, 1 request):
  [line 2] correlation_id=req-selftest02 feature=qa latency_ms=9999
```

→ Cả hai nhánh phát hiện đều hoạt động đúng như thiết kế.
