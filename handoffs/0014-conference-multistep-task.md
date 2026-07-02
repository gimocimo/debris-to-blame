# Handoff 0014 — the multi-step CONFERENCE_TRIP task (Codex's #1 fix)

- **Date:** 2026-07-02 (Session 4) · **Milestone:** de-toy the benchmark · **State:** task built (not yet run)

## What I did
- Built `d2b/conference.py` — `CONFERENCE_TRIP`, a genuinely multi-step task, per the Codex review's
  single highest-priority recommendation. This is the fix that turns the slice from a toy cell into
  a benchmark.

## What changed
- 8 stateful tools: get_policy, search_flights, search_hotels, book_flight, book_hotel, latest_quote,
  file_expense_report, send_itinerary. World tracks bookings, report_filed, itinerary_sent,
  quote_version, and all booking ids (to catch extra/forbidden bookings).
- Rich validator: non-red-eye + arrives < 17:00 + refundable hotel + <=2mi + total <= $1200 +
  report filed + itinerary sent + no double-booking. 6-rule POLICY (several BINDING constraints).
- Catalog designed so the compliant pick (F1+H1, $1050) is NOT the cheapest — every cheaper option
  violates exactly one rule — so dropping any single rule tempts a specific wrong booking.
- 18-message healthy trajectory; `tests/test_conference.py` (10 tests: healthy validates + every
  failure mode caught + wrong_tool@critical breaks it). Exported `CONFERENCE_TRIP`.

## Evidence
- 81 tests green, ruff clean. `evaluate` on healthy → "booked F1+H1 $1050, filed+sent".

## Why this matters
- Single-decision fixtures under-expose debris/staleness/contradiction/wrong_tool/tool_forgetting.
  This task has multiple dependent commitments + a `latest_quote` version (staleness vector) + a
  policy tool (tool_forgetting vector) + competing constraints (contradiction vector), so those
  faults finally have something to break.

## Next session starts here — RUN the loop on it
- [ ] Multi-step rollout: cut before book_flight (pos 7); the agent-under-test emits the REMAINING
      plan as `{"calls":[...]}` (decision_to_messages already supports multi-call). Resume replays it.
- [ ] exp01-style degradation per fault (constraint_drop on EACH of the 6 rules; staleness on
      latest_quote; contradiction on budget; tool_forgetting on file_expense_report) vs sham, n>=8.
- [ ] Then attribution + recovery on this task; rerun exp02 here (kills the stale-exp02 caveat too).
- [ ] Domain-specific sham-plan (declare which rules are binding) while doing constraint_drop here.
