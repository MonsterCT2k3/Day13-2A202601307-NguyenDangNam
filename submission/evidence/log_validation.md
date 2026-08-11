# Log validation evidence

Generated locally after running the API and `python scripts/load_test.py --concurrency 5`.

```text
--- Lab Verification Results ---
Total log records analyzed: 21
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 10
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 100/100
```

The generated log contains request IDs such as `req-ee7bcdcc` and redacted previews such as `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, and `[REDACTED_CREDIT_CARD]`.
