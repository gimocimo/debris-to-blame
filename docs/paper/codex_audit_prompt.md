# Codex prompt — full adversarial audit of debris-to-blame (experiments + results)

Paste everything below the line into a Codex session running in the repo root.

---

You are an **adversarial research auditor**. Your job is to try to break this repository's experiments
and results — to surface every mistake, statistical error, grader artifact, leakage, misinterpretation,
and over/under-claim — and to hand back a precise, actionable findings report that a coding agent
("Claude") will use to fix everything. Be skeptical and thorough. Do **not** rubber-stamp.

## Mindset & ground rules

- **Assume errors exist.** This project has already self-caught two contamination bugs — a leaked
  answer key in the attribution grader, and a self-labelling `(cached)` tell that made a "deception"
  fault detectable. Assume more lurk. Where a result looks impressive, get suspicious.
- **The owner prizes honesty over impressiveness.** A finding that shrinks a headline is *welcome*.
- **Every finding must be backed by evidence** — a `file:line`, a command you ran and its output, or a
  reproduction. Mark each finding `CONFIRMED` (you reproduced it) or `SUSPECTED` (argued but not
  reproduced). No vibes-only findings.
- **Do not trust the prose.** Docs (`README.md`, `docs/results.md`, `docs/paper/*.md`) make quantitative
  claims; verify each against the committed data by re-running the scorers and reading the raw JSON.
  If a doc number and the data disagree, that is a finding.
- **A clean area is a valid result** — if you check something and it holds, say so explicitly. Coverage
  matters as much as findings.
- **Do not edit the repo.** Report; Claude fixes. (You may create scratch files under `/tmp`.)

## What the project claims (so you know what to attack)

Thesis: inject typed faults into known-good agent trajectories → the blame label is correct *by
construction* → this makes failure **attribution** measurable without human annotation. The headline
finding is an **information ladder**: what an auditor needs to localize the cause of a failed run is
**fault-type-structured** — `trace only` → `+ outcome` → `+ reference policy` → `+ ground-truth state`.
Two "robust regimes": a **deletion gap** (a dropped rule; closed only by re-supplying the exact rule)
and a **deception gap** (stale data / misexecution; the policy does NOT close it). A key sub-claim:
"omission" faults were a *culpability-vs-causation* artifact — asking "why did this run fail?" instead
of "did the agent err?" closes them. All inference is Claude models at $0 via subagents.

## Orientation (read these first)

- Code: `d2b/` (domains `conference.py`, `scheduling.py`, `review.py`; `rollout.py` the ReAct loop +
  `Injector`; `faults.py` `redact_for_attribution`; `detective.py` `grade_attribution`; `stats.py`).
- Experiment drivers: `experiments/step.py` (rollout CLI), `experiments/attribute.py` (renders a trace
  for an auditor in arms `blind|deleak|policy|rootcause|rootcause_policy`), `conf_score.py`
  (degradation), `conf_attr_score.py` (attribution), `attr_baselines.py`, `conf_recover_score.py`,
  `attr_common.py` (`record_for` — the ground-truth key per condition).
- Committed data: `experiments/decisions/states*/` (rollout states — `{condition,domain,variant,
  decisions}`), `experiments/decisions/conf_attribution_alldomains.json` (363 auditor verdicts),
  `experiments/decisions/p3_*_verdicts.json`, `experiments/decisions/organic_p2/`.
- Narrative: `docs/results.md`, `docs/paper/framing.md`, `docs/paper/related_work.md`, `PROJECT_PLAN.md`
  (§9 decision log), `ROADMAP.md`, `handoffs/0018-*.md`.
- Everything is designed to replay deterministically from committed data with **no model calls**:
  `uv run python experiments/conf_score.py "experiments/decisions/states/*.json"` etc. Run
  `uv run --extra dev pytest -q` and `uv run --extra dev ruff check .` first.

## Audit checklist (necessary, not exhaustive — go beyond it)

**A. Reproducibility & data integrity.**
- Re-derive EVERY headline number below from the committed data. Flag any that doesn't match its doc.
- The master verdict file was built by appending several audit runs. Check for **duplicates** and
  **wrong denominators**: does each (domain, fault, arm) cell have the n it should (usually 8, or 24
  pooled over 3 domains)? Any verdict double-counted? Any left over from a *superseded* run (e.g.
  pre-`(cached)`-fix staleness verdicts still present)?
- **Hand-transcribed data (high risk):** 3 verdicts in the review-forget/policy cell were transcribed
  by Claude from async-agent outputs (search the git log / look for a "backfill" tag). Verify they
  exist, are labelled as backfilled, and are not silently inflating a rate. Flag any place where a
  human/agent *authored* a verdict rather than capturing a raw tool output.
- Are rate-limited/missing audits handled honestly (denominators reflect actual n, not the intended n)?

**B. Statistical validity.**
- `stats.cluster_by_variant`: the "variant is affected if fail-rate > 0.5" rule with 2 reps means "both
  reps failed". Is that a sound independent-unit definition? Is the variant-clustered Fisher
  (e.g. 4/4 vs 0/4 → p≈0.029) computed correctly, and is it the right test at this n?
- **Multiple comparisons:** many fault×domain Fisher tests are reported with no correction. Is the
  family-wise error acknowledged? Are any "p=.029" claims fragile (they are the *floor* at n=4 — a
  single flipped variant changes them)?
- Wilson intervals correct? Is any "8/8, p=.029" phrasing implying more power than 4 independent units give?

**C. Grader correctness (the whole result rests on this — scrutinize hardest).**
- Read `detective.grade_attribution` + `attr_common.record_for` + the `attr_keys` per fault. Are the
  keys **fair** — not so lenient they over-credit, not so strict they under-credit?
- **Re-grade a sample BY HAND.** Pull ~15 verdicts spanning misexec/rootcause, forget/rootcause, and
  staleness/rootcause from `conf_attribution_alldomains.json`; for each, decide yourself whether the
  `culprit` genuinely identifies the injected fault, and compare to what `grade_attribution` scores.
  Report the disagreement rate. **Specifically stress the misexec root-cause claim (23/24 "deduction
  by elimination"):** the keys include generic tokens like `wrong`, `instead`, `different`, `tool`,
  `mismatch`. Does a verdict that merely says "a tool must have done something different" get credited
  even if it does not correctly identify misexecution? Is 23/24 real, or a lenient-grader artifact?
- Does `forget`'s key set (`file`/`expense`/`report`, `post`/`agenda`, `close`/`ticket`) over-credit on
  generic words? Does misexec's inclusion of the wrong-item id (e.g. `F2`) risk crediting a verdict
  that names `F2` for an unrelated reason (note `F2` appears in healthy flight listings)?

**D. Leakage / contamination.**
- Confirm the auditor NEVER sees injection markers or ground-truth labels: trace `redact_for_attribution`
  and `render_trace_for_detective`. Does the `deleak` arm exclude *only* the dropped rule?
- The `rootcause` arm is deliberately told the run FAILED (outcome-informed). Confirm it does not ALSO
  leak the fault type or the culprit. Is telling the auditor "it failed" a fair experimental condition,
  or does the paper over-read what that buys? (The doc claims it bundles outcome+causation-question —
  check that caveat is stated and not quietly dropped.)
- **Staleness "true deception":** confirm the injected observation is genuinely indistinguishable from a
  real one — no residual tell (version number, phrasing, ordering) that an auditor could key on. If a
  tell remains, the "blind 0 / oracle 0" is not a clean deception result.

**E. Injector / world correctness.**
- **Misexecution** (`rewrite_args` in `rollout.py` + the per-domain `misexec_injector`): verify the
  world truly executes the *substituted* item while the agent is shown a success message for the
  *requested* item, and the validator judges the **true** state. Look for any inconsistency that would
  make the fault trivially detectable or make the world/observation incoherent.
- **Debris** leaves the true value intact (its 0/8 null should be because agents ignore junk, not
  because the injector no-ops). **Contradiction**'s 0/8 null — is the note actually present and
  actually conflicting, or a no-op?
- Do the variant **invariants** (`test_variants.py`, `test_scheduling.py`, `test_review.py`) actually
  guarantee "exactly one compliant solution / the trap is a genuine lure" for ALL variants incl.
  `conference_hard` and `conference_xhard`? Could any "degradation" be the task being unsolvable rather
  than the fault biting? (Check healthy passes on every variant used.)

**F. Claim-vs-data consistency (hunt for misinterpretation).**
- Cross-check EVERY number in `docs/results.md` (esp. the fault-map table, the four-arm attribution
  table, and the method-comparison table) against the scorers. Transcription errors are likely.
- "Deception gap replicates 3/3" — is this *staleness only*, or does the narrative silently fold in
  misexec? Are the two deception *types* claimed at the right strength (staleness: blind 0 AND oracle 0;
  misexec: blind ~0, oracle 0, but rootcause 23/24 — is the "gap" language consistent)?
- "Organic failures 6/6 attributed" — the verdicts are all `problem=true`, but does each `culprit`
  actually name the *agent's* error (booking without a valid quote / ignoring the over-budget quote),
  or merely flag *a* problem? "Flagged 6/6" ≠ "correctly attributed 6/6" — check the doc's wording.
- Recovery: verify `no_repair`/`blind_repair`/`targeted_repair` for conference AND scheduling, and that
  the localization-lift and clustered p match.

**G. Interpretation & over-claiming.**
- Is "attribution as deduction by elimination" a sound reading, or could the root-cause auditors be
  pattern-matching / hedging toward "the tool did something" on any hard case? Design a check (e.g. do
  they ALSO cry "tool misexecution" on *healthy* or *staleness* traces under the root-cause prompt? If
  so, the misexec 23/24 is partly a response bias — this would be a major finding).
- Challenge the external-validity argument ("environment faults are un-elicitable by definition, so
  their realism rests on infrastructure facts"). Is that a fair scoping of R2 or a dodge?
- Same-family generate-and-grade (R6): is anything circular in a way that undermines the ladder? Is the
  cross-tier evidence (Haiku/Sonnet/Opus) actually only on conference cdrop (i.e. thin)?
- Scan for any surviving over-claim: does anything still call M2/v0.1 "closed", or state "3 tiers"
  when only conference-cdrop has a tier panel, or quote a pooled p the code disowns?

**H. Prior-art honesty (best-effort; use web if available).**
- The novelty is finding-led because the *method* (injection→attribution labels) is prior art. Verify
  the cited IDs resolve to the claimed papers and that the diff in `related_work.md` is fair:
  AEGIS `2509.14295`, AgenTracer `2509.03312`, CAR `2606.08275`, ReliabilityBench `2601.06112`,
  Who&When `2505.00212`, TRAIL `2505.08638`. Flag any hallucinated citation.
- Does any of them (or work you know) actually pre-empt the **information-ladder** / **root-cause-by-
  elimination** claim? If so, that is the most important finding in this audit.

**I. Code & test quality.**
- Any test that is tautological or asserts nothing meaningful? Any experiment/scorer with a bug that
  would change a reported number? Any dead/legacy code (e.g. the `exp01–04` travel scripts) that is
  NOT clearly marked superseded and could mislead a reader?

## Headline numbers to validate (re-derive each; flag mismatches)

- Degradation (per domain, variant-clustered; healthy & sham 0/8 everywhere): staleness, misexec,
  forget all **8/8 (4/4 variants, p≈.029)** on all 3 domains; cdrop = conf 7/8 (p≈.14) / sched 8/8
  (p≈.029) / review 0/8 null; debris 0/8 all; contradiction conf 1/8, sched 0/8, review 0/8.
- Attribution (opus), pooled over 3 domains unless noted — blind / oracle / root-cause:
  staleness **0/24 / 0/24 / 18/24** (per-domain rootcause 8/8, 7/8, 3/8);
  misexec **1/24 / 0/24 / 23/24**;
  cdrop **0/15 / (deleak 0/15) / oracle 15/15** (rootcause = unrun);
  forget **9/24 / 14/24 / 24/24**; healthy & sham false-positive **0**.
- Baselines random/recency/keyword: ≈0 recall, **100% false-positive**.
- Stepwise (Who&When-style, blind): cdrop 0/8, forget 12/12, misexec 2/12, staleness 0/12.
- Recovery: conference and scheduling both localization-lift **+1.00**, clustered 4/4 vs 0/4, p≈.029.
- External validity: **2/28** organic failures elicited; 6/6 auditor verdicts flag them.

## Output format (make it actionable for Claude)

First: a one-paragraph **overall verdict** (is the central finding — the fault-type-structured
information ladder — supported by the data as written? what is its honest strength?).

Then a **findings list**, ranked most-severe first. For each finding:

- `severity`: blocker | major | minor | nit
- `category`: reproducibility | stats | grader | leakage | injector | claim-vs-data | interpretation |
  prior-art | code
- `status`: CONFIRMED | SUSPECTED
- `location`: `file:line` and/or the exact command you ran
- `problem`: one or two sentences — what is wrong
- `evidence`: the command output / quote / repro that proves it
- `fix`: a concrete instruction for Claude (what to change, or what experiment to re-run)

Then a **coverage note**: which checklist areas you verified as CLEAN (so we know what was actually
checked), and anything you could not check (and why).

Be exhaustive on correctness, validity, and honesty; ignore pure style. If the strongest thing you can
say is "the central claim holds and here are 3 places the write-up overstates its strength," say
exactly that.
