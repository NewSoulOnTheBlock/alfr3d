"""Credit Builder — shared library.

Native Python port of the ElizaOS @elizaos/plugin-credit-builder domain logic:
letter-type metadata, bureau addresses, the FICO audit heuristics, dispute
tracking, and the Lob certified-mail client. Scope: the operator's OWN credit
(single profile). Not legal or financial advice.

Data (profile + disputes) persists under ~/alfr3d/credit/ so it survives
container restarts on the mounted volume.
"""

import base64
import json
import os
import urllib.request
import urllib.error
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def _data_dir():
    d = os.path.join(os.path.expanduser("~/alfr3d"), "credit")
    os.makedirs(d, exist_ok=True)
    return d


def _profile_path():
    return os.path.join(_data_dir(), "profile.json")


def _disputes_path():
    return os.path.join(_data_dir(), "disputes.json")


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_profile():
    return _read_json(_profile_path(), None)


def save_profile(profile):
    _write_json(_profile_path(), profile)


def load_disputes():
    return _read_json(_disputes_path(), [])


def add_dispute(record):
    disputes = load_disputes()
    disputes.append(record)
    _write_json(_disputes_path(), disputes)
    return record


# ---------------------------------------------------------------------------
# Letter types (19) + bureau addresses  (ported from types.ts)
# ---------------------------------------------------------------------------

LETTER_TYPE_INFO = {
    "basic_bureau": {"id": 1, "name": "Basic Credit Bureau Dispute", "category": "FCRA", "legal_basis": "FCRA § 1681i", "target_type": "bureau"},
    "609_verification": {"id": 2, "name": "609 Verification Request", "category": "FCRA", "legal_basis": "FCRA § 609", "target_type": "bureau"},
    "611_reinvestigation": {"id": 3, "name": "611 Reinvestigation Demand", "category": "FCRA", "legal_basis": "FCRA § 611", "target_type": "bureau"},
    "method_of_verification": {"id": 4, "name": "Method of Verification Demand", "category": "FCRA", "legal_basis": "FCRA § 611(a)(6)", "target_type": "bureau"},
    "identity_theft": {"id": 5, "name": "Identity Theft Dispute", "category": "FCRA", "legal_basis": "FCRA § 605B", "target_type": "bureau"},
    "debt_validation": {"id": 6, "name": "Debt Validation Letter", "category": "FDCPA", "legal_basis": "FDCPA § 1692g", "target_type": "collector"},
    "cease_desist": {"id": 7, "name": "Cease and Desist Letter", "category": "FDCPA", "legal_basis": "FDCPA § 1692c(c)", "target_type": "collector"},
    "pay_for_delete": {"id": 8, "name": "Pay-for-Delete Letter", "category": "Negotiation", "legal_basis": "Negotiation", "target_type": "collector"},
    "goodwill": {"id": 9, "name": "Goodwill Removal Letter", "category": "Courtesy", "legal_basis": "Courtesy", "target_type": "creditor"},
    "direct_creditor": {"id": 10, "name": "Direct Creditor Dispute", "category": "FCRA", "legal_basis": "FCRA § 1681s-2(b)", "target_type": "creditor"},
    "chargeoff_removal": {"id": 11, "name": "Charge-Off Removal Request", "category": "Negotiation", "legal_basis": "Negotiation", "target_type": "creditor"},
    "unauthorized_inquiry": {"id": 12, "name": "Unauthorized Inquiry Removal", "category": "FCRA", "legal_basis": "FCRA § 1681b", "target_type": "bureau"},
    "hipaa_medical": {"id": 13, "name": "HIPAA Medical Debt Dispute", "category": "HIPAA", "legal_basis": "HIPAA + FDCPA", "target_type": "collector"},
    "statute_of_limitations": {"id": 14, "name": "Statute of Limitations Defense", "category": "State Law", "legal_basis": "State SOL", "target_type": "collector"},
    "intent_to_sue": {"id": 15, "name": "Intent to Sue Letter", "category": "FCRA/FDCPA", "legal_basis": "FCRA § 1681n", "target_type": "any"},
    "arbitration_election": {"id": 16, "name": "Arbitration Election", "category": "Contract", "legal_basis": "Federal Arbitration Act", "target_type": "creditor"},
    "billing_error": {"id": 17, "name": "Billing Error (FCBA)", "category": "FCBA", "legal_basis": "FCBA § 1666", "target_type": "creditor"},
    "breach_of_contract": {"id": 18, "name": "Breach of Contract Notice", "category": "Contract", "legal_basis": "State contract law", "target_type": "any"},
    "demand_letter": {"id": 19, "name": "Formal Demand Letter", "category": "General", "legal_basis": "Contract law", "target_type": "any"},
}

BUREAU_ADDRESSES = {
    "equifax": {"name": "Equifax Information Services LLC", "address_line1": "P.O. Box 740256", "city": "Atlanta", "state": "GA", "zip": "30374-0256"},
    "experian": {"name": "Experian", "address_line1": "P.O. Box 4500", "city": "Allen", "state": "TX", "zip": "75013"},
    "transunion": {"name": "TransUnion LLC Consumer Dispute Center", "address_line1": "P.O. Box 2000", "city": "Chester", "state": "PA", "zip": "19016"},
}


def resolve_letter_type(text):
    """Map free text to a letter type, mirroring sendDisputeAction's parser."""
    t = (text or "").lower()
    if "609" in t:
        return "609_verification"
    if "611" in t:
        return "611_reinvestigation"
    if "verification" in t or "method" in t:
        return "method_of_verification"
    if "identity" in t or "fraud" in t:
        return "identity_theft"
    if "validation" in t or "validate" in t:
        return "debt_validation"
    if "cease" in t or "stop" in t:
        return "cease_desist"
    if "pay for delete" in t or "pay-for-delete" in t:
        return "pay_for_delete"
    if "goodwill" in t:
        return "goodwill"
    if "direct" in t:
        return "direct_creditor"
    if "charge" in t and "off" in t:
        return "chargeoff_removal"
    if "inquiry" in t or "hard pull" in t:
        return "unauthorized_inquiry"
    if "medical" in t or "hipaa" in t:
        return "hipaa_medical"
    if "statute" in t or "expired" in t or "too old" in t:
        return "statute_of_limitations"
    if "sue" in t or "lawsuit" in t:
        return "intent_to_sue"
    if "arbitration" in t:
        return "arbitration_election"
    if "billing" in t or "unauthorized charge" in t:
        return "billing_error"
    return "basic_bureau"


# ---------------------------------------------------------------------------
# Credit audit  (ported from creditProfileService.runAudit)
# ---------------------------------------------------------------------------

def _assess_dispute_candidate(item):
    gain, prob, letter = 20, 0.50, "basic_bureau"
    kind = item.get("type")
    if kind == "late_payment":
        gain, prob = 30, (0.65 if item.get("dispute_reason") else 0.35)
        letter = "basic_bureau" if item.get("dispute_reason") else "goodwill"
    elif kind == "collection":
        gain, prob, letter = 45, 0.55, "debt_validation"
    elif kind == "chargeoff":
        gain, prob, letter = 40, 0.40, "chargeoff_removal"
    elif kind == "inquiry":
        gain, prob, letter = 8, 0.70, "unauthorized_inquiry"
    return {
        "item": item,
        "recommended_letter_type": letter,
        "estimated_score_gain": gain,
        "success_probability": prob,
        "priority_score": round(gain * prob * 10) / 10,
        "escalation_path": ["Basic Bureau Dispute", "609 Verification", "611 Reinvestigation",
                             "CFPB Complaint", "Intent to Sue", "FCRA Attorney"],
    }


def audit(profile):
    """Run the FICO-factor audit. Port of runAudit()."""
    score = profile.get("current_score") or 0
    phase = ("elite" if score >= 740 else "optimization" if score >= 670
             else "acceleration" if score >= 580 else "foundation")

    strengths, weaknesses = [], []

    otp = profile.get("on_time_payment_percent")
    if otp is not None:
        if otp >= 99:
            strengths.append({"factor": "payment_history", "description": "Near-perfect payment history", "impact": "high", "score_weight_percent": 35})
        elif otp < 95:
            weaknesses.append({"factor": "payment_history", "description": f"Payment history at {otp}% — late payments are the #1 score killer", "impact": "high", "score_weight_percent": 35})

    util = profile.get("utilization_percent")
    if util is None and profile.get("total_credit_limit"):
        util = (profile.get("total_balance") or 0) / profile["total_credit_limit"] * 100
    util_status = "excellent"
    if util is not None:
        if util <= 9:
            util_status = "excellent"
            strengths.append({"factor": "utilization", "description": f"Utilization at {util:.0f}% — optimal range", "impact": "high", "score_weight_percent": 30})
        elif util <= 30:
            util_status = "good"
        elif util <= 50:
            util_status = "fair"
            weaknesses.append({"factor": "utilization", "description": f"Utilization at {util:.0f}% — should be under 30%, ideal under 10%", "impact": "high", "score_weight_percent": 30})
        else:
            util_status = "critical"
            weaknesses.append({"factor": "utilization", "description": f"Utilization at {util:.0f}% — CRITICAL. Pay down immediately", "impact": "high", "score_weight_percent": 30})

    age = profile.get("average_account_age_months")
    if age is not None:
        if age >= 84:
            strengths.append({"factor": "age", "description": f"Average account age {age/12:.1f} years — excellent", "impact": "medium", "score_weight_percent": 15})
        elif age < 24:
            weaknesses.append({"factor": "age", "description": "Average account age under 2 years — need to let accounts age", "impact": "medium", "score_weight_percent": 15})

    types = profile.get("account_types") or []
    has_revolving = "revolving" in types
    has_installment = any(t in ("installment", "auto", "student", "personal", "mortgage") for t in types)
    missing = []
    if not has_revolving:
        missing.append("revolving")
    if not has_installment:
        missing.append("installment")
    if len(types) < 3:
        weaknesses.append({"factor": "mix", "description": f"Only {len(types)} account type(s) — FICO rewards variety", "impact": "low", "score_weight_percent": 10})

    inq = profile.get("hard_inquiries_last_12mo")
    if inq is not None and inq > 3:
        weaknesses.append({"factor": "inquiries", "description": f"{inq} hard inquiries in last 12 months — slow down applications", "impact": "low", "score_weight_percent": 10})

    disputable = sorted(
        (_assess_dispute_candidate(i) for i in (profile.get("negative_items") or []) if i.get("disputable") is not False),
        key=lambda c: c["priority_score"], reverse=True,
    )

    payment_status = ("perfect" if (otp or 0) >= 99 else "good" if (otp or 0) >= 95
                      else "needs_work" if (otp or 0) >= 85 else "poor")

    return {
        "score_phase": phase,
        "utilization_status": util_status,
        "payment_history_status": payment_status,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "disputable_items": disputable,
        "missing_account_types": missing,
        "recommended_actions": _recommend(profile, util_status, missing, disputable, inq),
    }


def _recommend(profile, util_status, missing, disputable, inq):
    """Prioritized action plan derived from the audit signals."""
    actions = []
    if util_status in ("fair", "critical"):
        actions.append({"action": "Pay down revolving balances to <10%", "estimated_score_impact": 40,
                        "cost": 0, "timeline_days": 30, "priority": 1, "phase": "acceleration",
                        "description": "Utilization is the biggest fast-moving lever after payment history."})
    for cand in disputable[:5]:
        info = LETTER_TYPE_INFO[cand["recommended_letter_type"]]
        actions.append({"action": f"Dispute: {cand['item'].get('creditor_name', 'item')} via {info['name']}",
                        "estimated_score_impact": cand["estimated_score_gain"], "cost": 9,
                        "timeline_days": 30, "priority": 2, "phase": "acceleration",
                        "description": f"{info['legal_basis']} · est. success {int(cand['success_probability']*100)}%"})
    for m in missing:
        actions.append({"action": f"Add a {m} account (e.g. secured card / credit-builder loan)",
                        "estimated_score_impact": 15, "cost": 0, "timeline_days": 90, "priority": 3,
                        "phase": "foundation", "description": "Improves credit mix (10% of FICO)."})
    if inq and inq > 3:
        actions.append({"action": "Pause new credit applications for 6–12 months",
                        "estimated_score_impact": 10, "cost": 0, "timeline_days": 180, "priority": 4,
                        "phase": "optimization", "description": "Let hard inquiries age off."})
    actions.sort(key=lambda a: (a["priority"], -a["estimated_score_impact"]))
    return actions


# ---------------------------------------------------------------------------
# Lob certified-mail client  (ported from lobMailService.ts)
# ---------------------------------------------------------------------------

class LobMailClient:
    BASE = "https://api.lob.com/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    @property
    def is_test(self):
        return self.api_key.startswith("test_")

    def _auth_header(self):
        return "Basic " + base64.b64encode((self.api_key + ":").encode()).decode()

    def _post(self, path, data, form=False):
        if form:
            body = urllib.parse.urlencode(data).encode()
            content_type = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            content_type = "application/json"
        req = urllib.request.Request(
            f"{self.BASE}{path}", method="POST", data=body,
            headers={"Authorization": self._auth_header(), "Content-Type": content_type},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise RuntimeError(f"Lob API error {e.code}: {detail}")

    def verify_address(self, address):
        return self._post("/us_verifications", {
            "primary_line": address["address_line1"], "city": address["city"],
            "state": address["state"], "zip_code": address["zip"],
        })

    def send_certified_letter(self, frm, to, html, description):
        data = {
            "description": description,
            "to[name]": to["name"], "to[address_line1]": to["address_line1"],
            "to[address_city]": to["city"], "to[address_state]": to["state"], "to[address_zip]": to["zip"],
            "from[name]": frm["name"], "from[address_line1]": frm["address_line1"],
            "from[address_city]": frm["city"], "from[address_state]": frm["state"], "from[address_zip]": frm["zip"],
            "file": html, "color": "false", "mail_type": "usps_first_class",
            "extra_service": "certified_return_receipt", "address_placement": "top_first_page",
        }
        return self._post("/letters", data, form=True)

    def generate_letter_html(self, letter_type, client, recipient, items):
        today = datetime.now().strftime("%B %-d, %Y") if os.name != "nt" else datetime.now().strftime("%B %d, %Y")
        info = LETTER_TYPE_INFO[letter_type]
        items_block = "".join(
            f"""
      <p style="margin-left:20px">
        <strong>Account:</strong> {i.get('creditor_name','')}<br>
        <strong>Account #:</strong> XXXX-{i.get('account_number_last4','XXXX')}<br>
        <strong>Reason:</strong> {i.get('dispute_reason','Information is inaccurate')}<br>
        <strong>Type:</strong> {i.get('type','')}
      </p>""" for i in items)
        header = f"""
      <div style="font-family:'Times New Roman',serif;font-size:12pt;line-height:1.6;max-width:6.5in;margin:0 auto">
        <p>{client['name']}<br>{client['address_line1']}<br>{client['city']}, {client['state']} {client['zip']}<br>
        SSN (last 4): XXX-XX-{client.get('ssn_last4','XXXX')}<br>DOB: {client.get('dob','[DOB]')}</p>
        <p>{today}</p>
        <p>{recipient['name']}<br>{recipient['address_line1']}<br>{recipient['city']}, {recipient['state']} {recipient['zip']}</p>"""
        body = f"""
      <p><strong>RE: {info['name']}</strong></p>
      <p>Dear Sir/Madam:</p>
      <p>Pursuant to my rights under {info['legal_basis']}, I am writing regarding the following account(s):</p>
      {items_block}
      <p>I request that you investigate this matter and correct or delete the inaccurate information within 30 days as required by law.</p>
      <p>Please provide written confirmation of the results of your investigation.</p>"""
        footer = f"""
        <p>Sincerely,</p><br><br>
        <p>{client['name']}</p>
        <p style="font-size:10pt;color:#666;margin-top:30px"><em>SENT VIA USPS CERTIFIED MAIL — RETURN RECEIPT REQUESTED</em></p>
      </div>"""
        return f"<html><body>{header}{body}{footer}</body></html>"

    def send_dispute(self, client, letter_type, target, items):
        info = LETTER_TYPE_INFO[letter_type]
        bureau = BUREAU_ADDRESSES[target]
        html = self.generate_letter_html(letter_type, client, bureau, items)
        frm = {k: client[k] for k in ("name", "address_line1", "city", "state", "zip")}
        result = self.send_certified_letter(frm, bureau, html, f"Credit Dispute #{info['id']} - {info['name']} - {target}")
        now = datetime.now(timezone.utc)
        return {
            "id": str(uuid.uuid4()), "letter_type": letter_type, "letter_name": info["name"],
            "target": target, "recipient_name": bureau["name"], "items_disputed": items,
            "sent_date": now.isoformat(),
            "response_deadline": (now + timedelta(days=30)).isoformat(),
            "escalation_date": (now + timedelta(days=35)).isoformat(),
            "status": "sent", "lob_letter_id": result.get("id"),
            "tracking_number": result.get("tracking_number"), "cost": result.get("price"),
        }

    def send_to_all_bureaus(self, client, letter_type, items):
        return [self.send_dispute(client, letter_type, b, items) for b in ("equifax", "experian", "transunion")]
