# Directive 009 — Comprehensive Mechanical Audit

**Type:** Documentation / Housekeeping
**From:** Planning instance (claude.ai)
**Date:** 2026-02-08

## Context

Eight directives have built the signal-domain tier, motor layer, calibration infrastructure, and planning system. Before crossing into the semantic domain (conscious layer), we need to audit the entire codebase for mechanical issues — inconsistencies, violations, dead code, gaps.

This directive produces a **raw audit report** with zero interpretation. The planning instance will analyze the findings in a separate session with fresh context, specifically looking for conceptual issues (circular reasoning, self-fulfilling prophecies, architectural fallacies) that are harder to see from inside the accumulated assumptions of eight directives.

This is a zero-code-change directive. Read everything, report everything, fix nothing.

## Read Before Starting

Read EVERY source file, test file, and documentation file in the repo. This is a full audit — no file is exempt.

- `planning/CURRENT.md` — current state
- `handoff/state.md` — planning notes (copy to `planning/009_mechanical_audit.md`)

## The Audit

Produce `handoff/009_audit_report.md` organized into the sections below. For each section, report raw findings. If a section has no findings, say "No issues found." Do not editorialize, do not suggest fixes, do not interpret significance. Just report what you see.

### Section 1: Interface Compliance

For every system (all 7), verify:

- [ ] Implements `BaseSystem` ABC correctly (process, repair_check, apoptotic_condition, tick_rate)
- [ ] `process()` signature matches: takes `SystemState`, returns `SystemState`
- [ ] `process()` does not mutate input state (returns new dict with spread)
- [ ] `repair_check()` returns bool
- [ ] `apoptotic_condition()` returns bool
- [ ] `tick_rate` returns one of the expected string values

Report any deviation per system.

### Section 2: State Flow Integrity

Trace the full state flow through the LangGraph:

1. What fields does `create_default_state()` initialize?
2. What fields does each system read from state?
3. What fields does each system write to state?
4. Are there any fields that are written but never read?
5. Are there any fields that are read but never written (except by initialization)?
6. Are there any fields in `SystemState` TypedDict that no system touches?
7. Does `GraphState` mirror `SystemState` correctly?

Produce a matrix: rows = state fields, columns = systems, cells = R (read), W (write), RW (both), or blank.

### Section 3: Write Access Violations

The architecture enforces:
- Only sleep writes to the orientational field (via WRITE_TOKEN)
- No system writes to the genetic layer at runtime
- Motor does not write to immune_log or signal_pattern_cache
- No motor→sensory feedback within a single cycle (motor output doesn't feed back to sensory in the same graph traversal)

For each constraint, verify it holds in the actual code. Report any violations or near-violations (e.g., a system having access to a write method even if it doesn't call it).

### Section 4: Type Consistency

Check every TypedDict definition against actual usage:

- `SystemState`: Are all fields present in every state dict that flows through the graph?
- `SignalReport`, `SignalFeatures`, `SignalClassification`, `SignalDelta`: Are all fields populated by sensory? Are consumers reading fields that exist?
- `ThreatAssessment`: Populated by immune, consumed by whom?
- `SubconsciousOutput`: Populated by subconscious, consumed by whom?
- `MotorOutput`: All fields populated by motor? `transform_magnitude` included in all paths?
- `CachedSignalPattern`: Structure matches what subconscious writes and reads?

Report any mismatches — fields defined but not populated, fields accessed but not defined, type mismatches.

### Section 5: Connection Matrix vs Graph Routing

Compare the connection matrix in the topology module against the actual LangGraph routing:

- Which connections defined in topology are actually implemented in the graph?
- Which connections in topology are NOT implemented? (Expected: some are Phase 2+)
- Are there any graph edges that don't have corresponding topology entries?
- Do connection weights in topology match any actual behavior, or are they purely declarative?

### Section 6: Test Coverage Analysis

For each source file under `src/agenetic/`:

- How many functions/methods exist?
- How many are directly tested?
- How many are only tested indirectly (through integration tests)?
- How many are untested?

For test files:
- Are there any tests that test implementation details rather than behavior?
- Are there any tests that are tautological (test passes by definition)?
- Are there any tests that could never fail given the current code?

Pay special attention to the calibration tests — do they actually test anything, or do they just record data? (Recording data is fine if that's the intent, but flag any that are labeled as tests but have no assertions.)

### Section 7: Dead Code and Unused Imports

- Unused imports in any file
- Functions/methods defined but never called
- Constants defined but never referenced
- Code paths that can never execute

### Section 8: Documentation vs Reality

For each claim in README.md, CLAUDE.md, docs/ARCHITECTURE.md, docs/architecture_amendment.md, docs/signal_report_structure.md, and docs/DIRECTIVES.md:

- Does the code actually do what the documentation says?
- Are there features described as implemented that are actually stubs?
- Are there features implemented that aren't documented?
- Are test counts accurate?
- Are system descriptions accurate?

### Section 9: Motor Strategy Audit

For each motor strategy:

1. What is the governing limb?
2. What is the target formula?
3. What text transformation does it apply?
4. Is the transformation deterministic? (Verify: no random, no time-dependent, no external state)
5. Does the transformation preserve the repair check constraints?
6. For strategies that DON'T register in calibration (Tarka, Māyāvāda, Ārēka, Svadharma): why not? Is the reason documented accurately in DEVLOG/planning entries?

### Section 10: Calibration Apparatus Integrity

Examine the round-trip test infrastructure:

1. Does `round_trip()` actually feed motor output back through sensory? (Verify the data flow, not just the function name)
2. Does `vary_single_limb()` actually vary only one limb? (Check that all others are at baseline)
3. Does the calibration sweep test all 18 limbs?
4. At three weight points (0.0, 0.5, 1.0)?
5. Are the deltas computed correctly (output features minus baseline features)?
6. Is there any place where the test infrastructure could produce misleading results?

### Section 11: Orientational Field Integrity

- Are all 18 limbs present with correct IDs (1-18)?
- Are all limb names consistent across field definition, motor constants, test references, and documentation?
- Is write access truly restricted to sleep's WRITE_TOKEN?
- Could any system bypass the write restriction?
- Do the limb IDs in motor match the limb IDs in the field?

### Section 12: Anything Else

Anything that doesn't fit the above categories but seems wrong, surprising, inconsistent, or worth flagging. This is the "I noticed something weird" section.

## Output

Produce `handoff/009_audit_report.md` with all 12 sections. Be thorough. Be honest. If something looks suspicious but you're not sure, flag it anyway with a note that you're uncertain.

## Documentation Updates

- **`planning/CURRENT.md`:** Update from repo inspection (no code changes, just audit completion)
- **`DEVLOG.md`:** Append Directive 009 entry noting audit was performed, link to audit report, no code changes
- Copy `handoff/state.md` to `planning/009_mechanical_audit.md`

## Verification Checklist

- [ ] `handoff/state.md` copied to `planning/009_mechanical_audit.md`
- [ ] `handoff/009_audit_report.md` exists with all 12 sections
- [ ] Every source file under `src/agenetic/` was examined
- [ ] Every test file was examined
- [ ] Every documentation file was examined
- [ ] State flow matrix produced
- [ ] Test coverage analysis produced
- [ ] No code files modified
- [ ] All 237 tests still pass (run to confirm nothing was accidentally changed)
- [ ] `planning/CURRENT.md` updated
- [ ] `DEVLOG.md` has Directive 009 entry
- [ ] Git commit and push completed
