---
name: credit-builder
description: Build and repair your own credit — audit your FICO profile, plan score improvements, generate and mail FCRA/FDCPA/ECOA dispute letters via certified mail, track 30-day response deadlines, and plan business credit (DUNS/PAYDEX). Use when the user asks to analyze their credit, dispute a negative item, send a dispute or 609/debt-validation letter, check dispute status, or build business credit.
---

# Credit Builder

Native port of the credit-building workflow: profile audit, dispute automation
(certified mail via Lob), deadline tracking, and business-credit planning. Scope
is **the operator's own credit** (a single stored profile).

> **Not legal or financial advice.** This helps the user exercise their own FCRA
> rights on their own credit. Only dispute items there is a good-faith basis to
> believe are inaccurate, incomplete, or unverifiable — **frivolous or knowingly
> false disputes are unlawful under the FCRA** and get dismissed.

Scripts live in this skill's `scripts/` directory. Run them with `python`; each
takes a single JSON argument and prints JSON.

## 1. Analyze — `scripts/analyze.py`

Build/update the profile and run the FICO-factor audit (payment history 35%,
utilization 30%, age 15%, mix 10%, inquiries 10%). Fields merge into the saved
profile, so you can fill it in over several turns.

```bash
python scripts/analyze.py '{"profile": {"name":"...","address_line1":"...","city":"...","state":"..","zip":"...","current_score":640,"utilization_percent":55,"on_time_payment_percent":96,"negative_items":[{"type":"collection","creditor_name":"ABC Collections","dispute_reason":"Not mine"}]}}'
```

Returns the saved profile plus an `audit` with `score_phase`, strengths,
weaknesses, `disputable_items` (ranked by priority = est. gain × success
probability), `missing_account_types`, and a prioritized `recommended_actions`
plan. Summarize this for the user before doing anything else.

## 2. Send a dispute — `scripts/send_dispute.py`

Generates the letter and mails it as **USPS Certified Mail, Return Receipt** via
Lob, then records a dispute with a 30-day deadline. **Requires `LOB_API_KEY`.**

```bash
python scripts/send_dispute.py '{"letter_type":"debt_validation","target":"equifax"}'
python scripts/send_dispute.py '{"text":"send a 609 to all 3 bureaus"}'
```

- Sender address + negative items come from the saved profile (or pass `items`).
- `target`: `equifax` | `experian` | `transunion`; or `"all": true` for all three.
- 19 `letter_type`s: `basic_bureau`, `609_verification`, `611_reinvestigation`,
  `method_of_verification`, `identity_theft`, `debt_validation`, `cease_desist`,
  `pay_for_delete`, `goodwill`, `direct_creditor`, `chargeoff_removal`,
  `unauthorized_inquiry`, `hipaa_medical`, `statute_of_limitations`,
  `intent_to_sue`, `arbitration_election`, `billing_error`, `breach_of_contract`,
  `demand_letter`.

**Cost & mode:** each real letter is ~$9 (~$27 for all three bureaus). If
`LOB_API_KEY` starts with `test_`, Lob mails nothing (safe to rehearse). This
step is **autonomous** — it does not pause for confirmation — so before running
it, tell the user which letter, which target(s), and the cost, and make sure the
dispute is well-founded.

## 3. Track deadlines — `scripts/check_disputes.py`

```bash
python scripts/check_disputes.py '{}'
```

Lists pending vs **overdue** disputes. An item the bureau fails to verify within
30 days must be deleted (FCRA § 611) — overdue disputes are escalation
opportunities (send `611_reinvestigation` / `method_of_verification`, or file a
CFPB complaint).

## Business credit (guidance)

For business credit, coach the user through the standard ladder — you don't need
a script:
1. Foundation: LLC/corp, EIN, business address/phone, business bank account.
2. Get a **D-U-N-S** number; open **net-30 vendor tradelines** that report.
3. Build **PAYDEX** by paying vendors early; graduate to store/fleet cards, then
   bank/SBA credit.
Store business fields in the profile's `business` object via `analyze.py`.

## Setup

Set `LOB_API_KEY` (from dashboard.lob.com) in the environment — e.g. in
`docker-compose.yml` under `environment:` or in `config.json`. Use a `test_` key
until you're ready to mail real letters. Profile and dispute history persist in
`~/alfr3d/credit/`.
