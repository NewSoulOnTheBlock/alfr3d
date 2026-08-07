#!/usr/bin/env python3
"""Intake a credit profile and run the FICO-factor audit.

Usage:
  python analyze.py '{"profile": { ...CreditProfile fields... }}'
  python analyze.py            # re-audit the already-saved profile

Merges the given profile fields into the saved profile (so you can build it up
incrementally), saves it, runs the audit, and prints {profile, audit} as JSON.
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

    profile = creditlib.load_profile() or {}
    incoming = payload.get("profile") or payload  # accept bare profile too
    if isinstance(incoming, dict):
        profile.update(incoming)

    if not profile:
        print(json.dumps({"error": "no profile provided or saved. Pass {\"profile\": {...}}."}))
        return 1

    creditlib.save_profile(profile)
    report = creditlib.audit(profile)
    print(json.dumps({"profile": profile, "audit": report}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
