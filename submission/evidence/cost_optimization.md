# Cost Optimization evidence — incident `cost_spike`

Giải pháp triển khai trong `app/mock_llm.py`:
1. **Cap output tokens**: `MAX_OUTPUT_TOKENS=180` — chặn output token vượt mức bình thường
   ngay cả khi `cost_spike` đang bật (bình thường `output_tokens *= 4` khi có incident).
2. **Response cache**: cache theo prompt text đã render; prompt trùng lặp trả lời ngay từ cache
   với `tokens_in = tokens_out = 0` (không tính phí sinh lại nội dung giống hệt).

Quy trình đo: bật `cost_spike`, chạy `python scripts/load_test.py` (10 query trong
`data/sample_queries.jsonl`), đọc `GET /metrics` ngay sau mỗi lần chạy.

## BEFORE — chưa tối ưu (chỉ có cap/cache tắt, đúng code gốc)

```json
{"traffic":10,"latency_p95":1478.0,"avg_cost_usd":0.0077,"total_cost_usd":0.0766,
 "tokens_in_total":410,"tokens_out_total":5028,"quality_avg":0.88}
```

## AFTER — đã cap output tokens (lượt chạy đầu, cache còn trống)

```json
{"traffic":10,"latency_p95":1191.0,"avg_cost_usd":0.0028,"total_cost_usd":0.0282,
 "tokens_in_total":410,"tokens_out_total":1800,"quality_avg":0.88}
```

→ **Giảm 63.2% total_cost_usd** (0.0766 → 0.0282 USD) và giảm 64.2% tokens_out
(5028 → 1800) chỉ nhờ hard cap, dù incident `cost_spike` vẫn đang bật.

## AFTER — chạy lại đúng 10 query đó lần 2 (cache đã warm)

```json
{"traffic":20,"latency_p95":1191.0,"avg_cost_usd":0.0014,"total_cost_usd":0.0282,
 "tokens_in_total":410,"tokens_out_total":1800,"quality_avg":0.88}
```

→ `total_cost_usd` **không đổi** sau khi xử lý thêm 10 request giống hệt lần trước
(0.0282 → 0.0282 USD, tức **+0 USD** cho toàn bộ traffic lặp lại) — độ trễ mỗi request
cũng giảm từ ~154ms xuống ~2-4ms nhờ cache hit, xác nhận cache hoạt động đúng.

## Kết luận

Kết hợp cap + cache giữ chi phí ổn định ở mức baseline ngay cả khi incident `cost_spike`
đang hoạt động, và loại bỏ hoàn toàn chi phí phát sinh từ traffic lặp lại (câu hỏi trùng).
