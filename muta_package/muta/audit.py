#!/usr/bin/env python3
"""MUTA Audit System - Verifies integrity and append-only properties of audit logs.

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

Verifies integrity, ordering, continuity, and duplicate event IDs.
Does not prove storage is physically immutable; pair with append-only/WORM storage,
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
from typing import Any, Iterable, Tuple

GENESIS = "0" * 64
REQUIRED = {"schema_version", "sequence", "event_id", "timestamp", "event", "prev_hash", "event_hash"}
HEX64 = set("0123456789abcdef")


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


def load_events(path: Path) -> Tuple[list[tuple[int, dict[str, Any]]], list]:
    """Load events from a JSONL file, returning (events, issues)."""
    events: list[tuple[int, dict[str, Any]]] = []
    issues = []
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for line_number, raw in enumerate(handle, 1):
                if not raw.strip():
                    issues.append({"line": line_number, "code": "blank-line",
                                   "message": "blank lines are not valid audit records"})
                    continue
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError as exc:
                    issues.append({"line": line_number, "code": "invalid-json",
                                   "message": exc.msg})
                    continue
                if not isinstance(value, dict):
                    issues.append({"line": line_number, "code": "record-type",
                                   "message": "record must be a JSON object"})
                    continue
                events.append((line_number, value))
    except OSError as exc:
        issues.append({"line": 0, "code": "read-error", "message": str(exc)})
    return events, issues


def validate(path: Path) -> list:
    """Validate a MUTA append-only JSONL audit log.

    Returns a list of issue dicts. Each issue has keys: line, code, message.
    An empty list means the log is valid.
    """
    records, issues = load_events(path)
    previous_hash = GENESIS
    previous_sequence: int | None = None
    seen_ids: set[str] = set()

    for line_number, event in records:
        missing = REQUIRED - event.keys()
        if missing:
            issues.append({"line": line_number, "code": "missing-field",
                           "message": ",".join(sorted(missing))})
            continue

        sequence = event["sequence"]
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            issues.append({"line": line_number, "code": "sequence-type",
                           "message": "sequence must be an integer"})
        else:
            expected = 1 if previous_sequence is None else previous_sequence + 1
            if sequence != expected:
                issues.append({"line": line_number, "code": "sequence-gap",
                               "message": f"expected {expected}, got {sequence}"})
            previous_sequence = sequence

        event_id = event["event_id"]
        if not isinstance(event_id, str) or not event_id:
            issues.append({"line": line_number, "code": "event-id",
                           "message": "event_id must be a non-empty string"})
        elif event_id in seen_ids:
            issues.append({"line": line_number, "code": "duplicate-event",
                           "message": f"duplicate event_id {event_id!r}"})
        else:
            seen_ids.add(event_id)

        prev_hash = event["prev_hash"]
        if not isinstance(prev_hash, str) or len(prev_hash) != 64 or any(
                char not in HEX64 for char in prev_hash):
            issues.append({"line": line_number, "code": "prev-hash-format",
                           "message": "prev_hash must be 64 lowercase hexadecimal characters"})
        elif prev_hash != previous_hash:
            issues.append({"line": line_number, "code": "chain-break",
                           "message": f"expected previous hash {previous_hash}, got {prev_hash}"})

        supplied_hash = event["event_hash"]
        if not isinstance(supplied_hash, str) or len(supplied_hash) != 64 or any(
                char not in HEX64 for char in supplied_hash):
            issues.append({"line": line_number, "code": "event-hash-format",
                           "message": "event_hash must be 64 lowercase hexadecimal characters"})
        else:
            computed_hash = calculate_event_hash(event)
            if not hmac.compare_digest(supplied_hash, computed_hash):
                issues.append({"line": line_number, "code": "hash-mismatch",
                               "message": f"computed hash {computed_hash}, got {supplied_hash}"})

        if "computed_hash" in dir():
            previous_hash = computed_hash

    if not records and not issues:
        issues.append({"line": 0, "code": "empty-log", "message": "audit log contains no records"})
    return issues