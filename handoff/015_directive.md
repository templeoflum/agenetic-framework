# Directive 015 — Mechanical Audit: Read Everything, Report Raw

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-10

## Context

Read these files first, in this order:
1. `planning/CURRENT.md` — factual snapshot of where things stand
2. `CLAUDE.md` — project conventions, agent roles, directive protocol
3. `docs/ARCHITECTURE.md` — the v2 specification
4. `docs/architecture_amendment.md` — the signal-semantics boundary
5. `references/asparsa_limbs.md` — the 18 limb principles
6. `references/conceptual_archaeology.md` — Section V, limb-to-feature mapping

Then read every source file and every test file, in order. This is the audit.

**What happened before this directive:**

Directives 001–014 built the complete system:
- Signal domain: sensory, immune, subconscious, motor, orientational field, graph routing, round-trip calibration (001–010)
- Conscious layer: ConsciousOutput, gate, Deliberator protocol, Anthropic deliberator, graduated prompt assembly with limb interactions, observation harness (011–012)
- Motor codec: TextCodec extraction behind Codec protocol (013)
- Integration: conditional escalation, conscious-motor wiring, three end-to-end paths (014)
- 320 tests passing + 2 skipped

**What this directive is:**

A mechanical audit. You read every file, report what you find, and produce zero code changes. No fixes, no improvements, no refactoring. Your job is to be the project's eyes — read everything systematically and report factual observations.

The planning instance (claude.ai) and the conceptual audit (Directive 016) will evaluate your observations. You report; they judge.

**What this directive is NOT:**

- NOT a code review (no "this should be refactored")
- NOT a conceptual audit (no "this limb mapping is questionable")
- NOT remediation (no code changes)
- NOT approval or rejection (no "this passes" or "this fails")

## Objective

Read every source file and test file in the repository. For each file, report: what it contains, what it does, how it connects to other files, and any factual observations (not judgments). Produce a single comprehensive report.

## Audit Procedure

### Phase 1: Architecture Documents

Read and summarize (1–3 sentences each):
- `docs/ARCHITECTURE.md`
- `docs/architecture_amendment.md`
- `references/asparsa_limbs.md`
- `references/conceptual_archaeology.md`

### Phase 2: Source Files

For each file in `src/agenetic/`, read and report:

1. **File:** path and approximate LOC
2. **Purpose:** one sentence
3. **Exports:** what other files import from this file
4. **Imports:** what this file imports from other project files (not stdlib/third-party)
5. **Key data:** constants, types, or structures defined
6. **Connections:** which other files it directly interacts with at runtime
7. **Observations:** factual notes — NOT judgments. Examples:
   - "This function is called by X but the return value is not used by Y"
   - "This constant is defined here and also in file Z"
   - "This dict has 13 entries; the architecture doc says 18 limbs exist"
   - "This threshold (0.7) is hardcoded; no configuration mechanism exists"

Read files in this order:
1. `src/agenetic/systems/base.py`
2. `src/agenetic/field/orientational.py`
3. `src/agenetic/systems/sensory.py`
4. `src/agenetic/systems/immune.py`
5. `src/agenetic/systems/subconscious.py`
6. `src/agenetic/systems/conscious.py`
7. `src/agenetic/systems/deliberator.py`
8. `src/agenetic/systems/deliberator_anthropic.py`
9. `src/agenetic/systems/prompt_assembly.py`
10. `src/agenetic/systems/codec.py`
11. `src/agenetic/systems/text_codec.py`
12. `src/agenetic/systems/motor.py`
13. `src/agenetic/systems/sleep.py`
14. `src/agenetic/systems/genetic.py`
15. `src/agenetic/network/graph.py`
16. `src/agenetic/network/topology.py` (if it exists)

### Phase 3: Test Files

For each test file, read and report:
1. **File:** path and test count
2. **What it tests:** one sentence
3. **Coverage gaps:** systems, functions, or paths that have NO tests
4. **Observations:** factual notes about test structure

Read files in this order:
1. `tests/test_systems.py`
2. `tests/test_graph.py`
3. `tests/test_topology.py`
4. `tests/test_motor.py`
5. `tests/test_round_trip.py`
6. `tests/test_conscious.py`
7. `tests/test_prompt_assembly.py`
8. `tests/test_codec.py`
9. `tests/test_integration.py`

### Phase 4: Cross-Cutting Observations

After reading all files, report on these specific dimensions:

**A. Type flow:** Trace how data flows from input to output through the graph. What type is `state["input"]` at each stage? What type is `state["conscious_output"]` when motor reads it? Are there any untyped or loosely-typed handoffs?

**B. Limb coverage:** Which of the 18 limbs are referenced in code? Which are not? For each limb referenced, where is it referenced (which files, which functions)? Create a table: limb_id | limb_name | referenced_in_files.

**C. Threshold inventory:** List every hardcoded threshold in the codebase (e.g., 0.7, 0.5, 0.3, 1.5). For each: file, function, value, what it gates.

**D. Import graph:** List every import relationship between project files. Which files are imported by the most other files? Which files import the most?

**E. Test surface:** For each source file, count how many test files exercise it (directly or indirectly). Are there source files with zero test coverage?

**F. Dead code:** Are there any functions, classes, or constants that are defined but never imported or called by any other file?

**G. Consistency:** Are naming conventions consistent? (e.g., limb names: "Tarka" vs "tarka" vs "TARKA_ID"). Are dict key names consistent across files?

## Output

Produce a single file: `handoff/015_response.md`

Structure:
1. Summary (test count, file count, LOC count)
2. Architecture document summaries
3. Source file reports (one section per file)
4. Test file reports (one section per file)
5. Cross-cutting observations (A–G)
6. Raw observation list (every factual observation, numbered, no judgments)

## Scope Boundaries

**DO:**
- Read every source and test file
- Report factual observations
- Create the audit report

**DO NOT:**
- Change any code
- Change any test
- Change any documentation
- Make judgments or recommendations
- Create or modify any file except `handoff/015_response.md`, `handoff/state.md`, `planning/015_mechanical_audit.md`, `planning/CURRENT.md`
- Update DEVLOG.md or README.md (this directive produces no code changes)

**Exception:** CURRENT.md should be updated ONLY if the previous directive's update was inaccurate. If CURRENT.md is accurate, leave it unchanged.

## Deliverables

| File | Action |
|------|--------|
| `handoff/015_response.md` | Created — the complete audit report |
| `handoff/state.md` | Provided — planning notes |
| `planning/015_mechanical_audit.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Unchanged (or corrected if inaccurate) |
| `handoff/015_directive.md` | This file |

## Verification Checklist

- [ ] Every source file in `src/agenetic/` has been read and reported
- [ ] Every test file in `tests/` has been read and reported
- [ ] Architecture documents have been summarized
- [ ] Cross-cutting observations A–G are all present
- [ ] Raw observation list is numbered and factual (no judgments)
- [ ] Zero code changes
- [ ] Zero test changes
- [ ] Zero documentation changes (except CURRENT.md correction if needed)
- [ ] `handoff/state.md` copied to `planning/015_mechanical_audit.md`
- [ ] Git commit and push completed
