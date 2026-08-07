#!/usr/bin/env python3
"""Generate and send a certified dispute letter via Lob (autonomous).

Usage:
  python send_dispute.py '{"letter_type": "609_verification", "target": "equifax"}'
  python send_dispute.py '{"text": "send a debt validation to all 3 bureaus"}'
  python send_dispute.py '{"letter_type": "basic_bureau", "all": true, "items": [ ... ]}'

Requires LOB_API_KEY in the environment. Uses the saved profile for the sender
address and (if "items" is omitted) its negative_items. This sends real
certified mail unless LOB_API_KEY starts with "test_" (Lob test mode mails
nothing). Each real letter costs ~$9; sending to all 3 bureaus ~$27.

NOTE: this is fully autonomous by design — it does not pause for confirmation.
Only dispute information you have a good-faith basis to believe is inaccurate;
frivolous disputes are unlawful under the FCRA and can be dismissed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import creditlib


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "{}"
    try:
        payload = json.loads(arg) if arg.strip() else {}
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"invalid JSON argument: {e}"}))
        return 1

    api_key = os.environ.get("LOB_API_KEY")
    if not api_key:
        print(json.dumps({"error": "LOB_API_KEY is not set. Add it to your environment/config to send letters."}))
        return 1

    profile = creditlib.load_profile()
    if not profile:
        print(json.dumps({"error": "no saved profile. Run analyze.py with your profile first."}))
        return 1
    for field in ("name", "address_line1", "city", "state", "zip"):
        if not profile.get(field):
            print(json.dumps({"error": f"profile is missing required sender field '{field}'."}))
            return 1

    letter_type = payload.get("letter_type") or creditlib.resolve_letter_type(payload.get("text", ""))
    if letter_type not in creditlib.LETTER_TYPE_INFO:
        print(json.dumps({"error": f"unknown letter_type '{letter_type}'.", "valid": list(creditlib.LETTER_TYPE_INFO)}))
        return 1

    text = (payload.get("text") or "").lower()
    send_all = bool(payload.get("all")) or any(k in text for k in ("all bureau", "all 3", "all three"))
    target = payload.get("target") or ("experian" if "experian" in text else "transunion" if "transunion" in text else "equifax")

    items = payload.get("items")
    if not items:
        items = (profile.get("negative_items") or [])[:3] or [
            {"type": "other", "creditor_name": "Unknown", "dispute_reason": "Information is inaccurate"}
        ]

    client = creditlib.LobMailClient(api_key)
    info = creditlib.LETTER_TYPE_INFO[letter_type]
    try:
        if send_all:
            records = client.send_to_all_bureaus(profile, letter_type, items)
        else:
            records = [client.send_dispute(profile, letter_type, target, items)]
    except Exception as e:
        print(json.dumps({"error": str(e), "hint": "Check LOB_API_KEY and that billing is enabled at dashboard.lob.com"}))
        return 1

    for r in records:
        creditlib.add_dispute(r)

    print(json.dumps({
        "status": "sent",
        "test_mode": client.is_test,
        "letter": info["name"],
        "legal_basis": info["legal_basis"],
        "count": len(records),
        "records": [{"target": r["target"], "lob_letter_id": r["lob_letter_id"],
                     "tracking_number": r["tracking_number"], "response_deadline": r["response_deadline"],
                     "cost": r["cost"]} for r in records],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
