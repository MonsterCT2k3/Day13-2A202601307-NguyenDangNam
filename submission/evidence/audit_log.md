# Audit log evidence

Module `app/audit.py` ghi mỗi sự kiện enable/disable incident vào file riêng
`AUDIT_LOG_PATH` (mặc định `data/audit.jsonl`, tách biệt hoàn toàn khỏi `data/logs.jsonl`),
được gọi từ `POST /incidents/{name}/enable` và `POST /incidents/{name}/disable`
trong `app/main.py`.

Sinh dữ liệu bằng cách bật/tắt lần lượt 3 incident (`rag_slow`, `cost_spike`, `tool_fail`)
qua `python scripts/inject_incident.py --scenario <name>` và `--disable`.

Nội dung `data/audit.jsonl` sau khi chạy:

```json
{"ts": "2026-08-11T08:01:30Z", "event": "incident_enabled", "name": "rag_slow"}
{"ts": "2026-08-11T08:01:30Z", "event": "incident_disabled", "name": "rag_slow"}
{"ts": "2026-08-11T08:01:31Z", "event": "incident_enabled", "name": "cost_spike"}
{"ts": "2026-08-11T08:01:31Z", "event": "incident_disabled", "name": "cost_spike"}
{"ts": "2026-08-11T08:01:31Z", "event": "incident_enabled", "name": "tool_fail"}
{"ts": "2026-08-11T08:01:31Z", "event": "incident_disabled", "name": "tool_fail"}
```

File này bị `.gitignore` (giống `data/logs.jsonl`) vì là dữ liệu runtime cục bộ,
không commit vào repo — evidence trên chứng minh cơ chế hoạt động đúng.
