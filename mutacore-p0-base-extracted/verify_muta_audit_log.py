#!/usr/bin/env python3
"""Verify integrity and append-only properties of a MUTA audit log.

Expected JSONL event shape:
{
  "schema_version": 1,
  "sequence": 1,
  "event_id": "uuid",
  "timestamp": "2026-09-12T18:00:00Z",
  "event": "execution.started",
  "payload": {"...": "..."},
  "prev_hash": "0" * 64,
  "event_hash": "<sha256(canonical event without event_hash)>"
}

This verifies integrity, ordering, continuity, and duplicate event IDs. It does
not prove storage is physically immutable; pair it with append-only/WORM storage,
access control, signatures, and independent anchoring for stronger assurance.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

GENESIS = "0" * 64
REQUIRED = {"schema_version", "sequence", "event_id", "timestamp", "event", "prev_hash", "event_hash"}
HEX64 = set("0123456789abcdef")


@dataclass(frozen=True)
class Issue:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"line={self.line} code={self.code} {self.message}"


def canonical_json(value: Any) -> bytes:
    """Serialize deterministically; never use a language-specific repr."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def calculate_event_hash(event: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in event.items() if key != "event_hash"}
    return hashlib.sha256(canonical_json(unsigned)).hexdigest()


def load_events(path: Path) -> tuple[list[tuple[int, dict[str, Any]]], list[Issue]]:
    events: list[tuple[int, dict[str, Any]]] = []
    issues: list[Issue] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for line_number, raw in enumerate(handle, 1):
                if not raw.strip():
                    issues.append(Issue(line_number, "blank-line", "blank lines are not valid audit records"))
                    continue
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError as exc:
                    issues.append(Issue(line_number, "invalid-json", f"{exc.msg}"))
                    continue
                if not isinstance(value, dict):
                    issues.append(Issue(line_number, "record-type", "record must be a JSON object"))
                    continue
                events.append((line_number, value))
    except OSError as exc:
        issues.append(Issue(0, "read-error", str(exc)))
    return events, issues


def validate(path: Path) -> list[Issue]:
    records, issues = load_events(path)
    previous_hash = GENESIS
    previous_sequence: int | None = None
    seen_ids: set[str] = set()

    for line_number, event in records:
        missing = REQUIRED - event.keys()
        if missing:
            issues.append(Issue(line_number, "missing-field", ",".join(sorted(missing))))
            continue

        sequence = event["sequence"]
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            issues.append(Issue(line_number, "sequence-type", "sequence must be an integer"))
        else:
            expected = 1 if previous_sequence is None else previous_sequence + 1
            if sequence != expected:
                issues.append(Issue(line_number, "sequence-gap", f"expected {expected}, got {sequence}"))
            previous_sequence = sequence

        event_id = event["event_id"]
        if not isinstance(event_id, str) or not event_id:
            issues.append(Issue(line_number, "event-id", "event_id must be a non-empty string"))
        elif event_id in seen_ids:
            issues.append(Issue(line_number, "duplicate-event", f"duplicate event_id {event_id!r}"))
        else:
            seen_ids.add(event_id)

        prev_hash = event["prev_hash"]
        if not isinstance(prev_hash, str) or len(prev_hash) != 64 or any(char not in HEX64 for char in prev_hash):
            issues.append(Issue(line_number, "prev-hash-format", "prev_hash must be 64 lowercase hexadecimal characters"))
        elif prev_hash != previous_hash:
            issues.append(Issue(line_number, "chain-break", f"expected previous hash {previous_hash}, got {prev_hash}"))

        supplied_hash = event["event_hash"]
        if not isinstance(supplied_hash, str) or len(supplied_hash) != 64 or any(char not in HEX64 for char in supplied_hash):
            issues.append(Issue(line_number, "event-hash-format", "event_hash must be 64 lowercase hexadecimal characters"))
            computed_hash = None
        else:
            computed_hash = calculate_event_hash(event)
            if not hmac.compare_digest(supplied_hash, computed_hash):
                issues.append(Issue(line_number, "hash-mismatch", f"computed hash {computed_hash}, got {supplied_hash}"))

        if computed_hash is not None:
            previous_hash = computed_hash

    if not records and not issues:
        issues.append(Issue(0, "empty-log", "audit log contains no records"))
    return issues


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a MUTA append-only JSONL audit log")
    parser.add_argument("log", type=Path, help="path to the UTF-8 JSONL audit log")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit machine-readable result")
    args = parser.parse_args(argv)

    issues = validate(args.log)
    result = {"log": str(args.log), "ok": not issues, "issues": [issue.__dict__ for issue in issues]}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        if issues:
            print(f"FAIL: {args.log}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"OK: {args.log}: chain, ordering, continuity and event IDs verified")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
