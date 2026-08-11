"""Quét data/logs.jsonl để tự động phát hiện PII leak và request vi phạm SLO latency."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml

from app.cli import configure_utf8_stdio
from app.pii import PII_PATTERNS

DEFAULT_LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
DEFAULT_SLO_PATH = REPO_ROOT / "config" / "slo.yaml"


def load_latency_threshold_ms(slo_path: Path) -> float:
    data = yaml.safe_load(slo_path.read_text(encoding="utf-8"))
    return float(data["slis"]["latency_p95_ms"]["objective"])


def find_pii_leaks(log_path: Path) -> list[dict]:
    leaks: list[dict] = []
    for lineno, raw_line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        for name, pattern in PII_PATTERNS.items():
            for match in re.finditer(pattern, line):
                window_start = max(0, match.start() - 15)
                if "REDACTED" in line[window_start:match.start()]:
                    continue  # đã được scrub_text() che, không tính là leak
                leaks.append({"line": lineno, "pattern": name, "match": match.group(0)})
    return leaks


def find_latency_violations(log_path: Path, threshold_ms: float) -> list[dict]:
    violations: list[dict] = []
    for lineno, raw_line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") == "response_sent" and record.get("latency_ms", 0) > threshold_ms:
            violations.append(
                {
                    "line": lineno,
                    "correlation_id": record.get("correlation_id"),
                    "feature": record.get("feature"),
                    "latency_ms": record.get("latency_ms"),
                }
            )
    return violations


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH))
    parser.add_argument("--slo", default=str(DEFAULT_SLO_PATH))
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Không tìm thấy log tại {log_path}")
        return 1

    threshold_ms = load_latency_threshold_ms(Path(args.slo))
    leaks = find_pii_leaks(log_path)
    violations = find_latency_violations(log_path, threshold_ms)

    print(f"--- Anomaly Detection Report ({log_path}) ---")
    print(f"PII leaks detected: {len(leaks)}")
    for leak in leaks:
        print(f"  [line {leak['line']}] pattern={leak['pattern']} match={leak['match']!r}")
    print(f"Latency SLO violations (> {threshold_ms:.0f} ms, {len(violations)} request):")
    for v in violations:
        print(
            f"  [line {v['line']}] correlation_id={v['correlation_id']} "
            f"feature={v['feature']} latency_ms={v['latency_ms']}"
        )

    if leaks or violations:
        print("\n[ALERT] Phát hiện anomaly trong log.")
        return 1
    print("\nKhông phát hiện anomaly nào.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
