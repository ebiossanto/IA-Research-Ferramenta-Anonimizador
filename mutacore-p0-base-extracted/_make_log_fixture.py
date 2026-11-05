import json
from pathlib import Path
from verify_muta_audit_log import GENESIS, calculate_event_hash

records = []
previous = GENESIS
for sequence, name in ((1, "execution.started"), (2, "execution.finished")):
    event = {
        "schema_version": 1,
        "sequence": sequence,
        "event_id": f"fixture-{sequence}",
        "timestamp": f"2026-09-12T18:00:0{sequence}Z",
        "event": name,
        "payload": {"execution_id": "fixture-exec"},
        "prev_hash": previous,
    }
    event["event_hash"] = calculate_event_hash(event)
    records.append(event)
    previous = event["event_hash"]
Path("/tmp/muta-valid.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
records[1]["payload"]["execution_id"] = "tampered"
Path("/tmp/muta-tampered.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
