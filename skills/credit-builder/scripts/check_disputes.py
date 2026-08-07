#!/usr/bin/env python3
"""Report dispute status: pending, overdue, and resolved.

Usage:
  python check_disputes.py

A dispute is "overdue" once its 30-day response deadline has passed while still
in a sent/delivered state — by the FCRA, an item the bureau fails to verify in
time must be deleted, so overdue disputes are your escalation opportunities.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import creditlib


def main():
    disputes = creditlib.load_disputes()
    now = datetime.now(timezone.utc)

    def deadline(d):
        try:
            return datetime.fromisoformat(d["response_deadline"])
        except Exception:
            return now

    pending, overdue, other = [], [], []
    for d in disputes:
        if d.get("status") in ("sent", "delivered"):
            (overdue if deadline(d) <= now else pending).append(d)
        else:
            other.append(d)

    def summarize(d):
        return {"letter": d.get("letter_name"), "target": d.get("target"),
                "status": d.get("status"), "response_deadline": d.get("response_deadline"),
                "lob_letter_id": d.get("lob_letter_id"), "tracking_number": d.get("tracking_number")}

    print(json.dumps({
        "total": len(disputes),
        "pending": [summarize(d) for d in pending],
        "overdue": [summarize(d) for d in overdue],
        "resolved_or_other": [summarize(d) for d in other],
        "note": "Overdue disputes passed the 30-day FCRA window — escalate (611, CFPB complaint, or MOV demand).",
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
