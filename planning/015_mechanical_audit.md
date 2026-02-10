# 015 — Mechanical Audit

Date: 2026-02-10
Directive type: Audit (zero code changes)

## What This Directive Does

DNAgent reads every file in the project and produces a factual report. No fixes, no judgments, no recommendations. Raw observations only. The planning instance and Directive 016 (conceptual audit) evaluate the observations.

## Why This Exists

The build agent that wrote the code can't audit its own work objectively. But it CAN read everything systematically and report what's there. Factual reporting is within its competence — it's just pattern matching and enumeration. The conceptual evaluation requires fresh eyes (016).

The mechanical audit produces the data that the conceptual audit interprets. Without 015's inventory, 016 would have to do its own file reading AND its own evaluation, which is too much scope for one directive.

## What the Report Should Contain

Seven cross-cutting analyses:
- **Type flow:** How data moves through the graph, what types at each handoff
- **Limb coverage:** Which of 18 limbs appear in code, where
- **Threshold inventory:** Every hardcoded number and what it gates
- **Import graph:** Dependency relationships between files
- **Test surface:** Coverage per source file
- **Dead code:** Defined but never used
- **Consistency:** Naming conventions, key names across files

Plus per-file reports for all source and test files.

## What to Watch

- The agent might slip into judgment mode ("this threshold should be configurable"). The directive explicitly says factual observations only. If the report contains recommendations, those should be flagged during review but don't invalidate the factual content.

- The report will be long. That's expected — it's an inventory of a 320-test codebase with ~3000+ LOC across 15+ source files.

- The threshold inventory is the most valuable section for 016. Every hardcoded number is a design decision that the conceptual audit needs to evaluate.

## Broader Roadmap

011 ✓ ConsciousOutput type, gate, Deliberator protocol. 262 tests.
012 ✓ Prompt assembly refinement. 292 tests.
013 ✓ Motor codec refactor. 304 tests.
014 ✓ Integration wiring. 320 tests.
015 — **This directive.** Mechanical audit. Zero code changes.
016 — Conceptual audit. Fresh planning instance, adversarial posture.
017 — Remediation.
