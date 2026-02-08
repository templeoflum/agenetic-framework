# Directive 006 — Planning Infrastructure Migration

**Type:** Refactoring / Documentation
**From:** Planning instance (claude.ai)
**Date:** 2026-02-08

## Context

The monolithic PLANNING_LOG.md has been rewritten from scratch four times in five directives. It doesn't scale — every planning session requires carrying the entire history of rationale forward. This directive migrates to an entry-based system that separates focused planning notes from cumulative state.

This is a zero-code-change directive. No new features, no test changes, no source modifications. Infrastructure only.

## The New Pattern

Going forward, each directive cycle the planning instance drops two files into `handoff/`:

1. **Directive file** (`NNN_directive.md`) — what to build
2. **State file** (`state.md`) — planning notes for this cycle: decisions made, observations, rationale, sequencing

`state.md` is always the same filename — each cycle overwrites the previous one. It's a transient exchange document, not a permanent record.

DNAgent's responsibilities with the state file:

1. Save a copy as `planning/NNN_<short_name>.md` (the permanent entry — never overwritten)
2. Extract factual current state into `planning/CURRENT.md` (the slim snapshot)

`CURRENT.md` is the only file that gets rewritten each directive. It contains only ground truth: test count, system status, active blockers, last directive summary, next candidates. No rationale, no analysis. DNAgent populates it from actual repo inspection, so it's always accurate.

The planning instance reads `CURRENT.md` to orient at the start of each cycle. Numbered entries are referenced when deeper context is needed.

## Read Before Starting

- `PLANNING_LOG.md` — the current monolith (will be moved)
- `CLAUDE.md` — needs updated project structure and workflow description
- `docs/DIRECTIVES.md` — needs updated to describe state file handling
- `DEVLOG.md` — append entry

## Part A: Create Planning Directory Structure

```
planning/
├── CURRENT.md                          # DNAgent maintains — factual snapshot
├── 001_through_005_legacy.md           # archived monolith
└── 006_planning_infrastructure.md      # first entry in new format (provided below)
```

1. Create `planning/` directory
2. Move `PLANNING_LOG.md` → `planning/001_through_005_legacy.md`
3. Remove `PLANNING_LOG.md` from root (it now lives in `planning/`)
4. Copy `handoff/state.md` → `planning/006_planning_infrastructure.md` (first entry in new format)

## Part B: Create CURRENT.md

Create `planning/CURRENT.md` by inspecting the actual repo state. Use this template:

```markdown
# Current State

**Last updated:** [date] (post-Directive [N])
**Tests:** [run pytest, report actual count]

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | [implemented/stub] | [count] |
| Immune | [implemented/stub] | [count] |
| Subconscious | [implemented/stub] | [count] |
| Conscious | [implemented/stub] | [count] |
| Motor | [implemented/stub] | [count] |
| Sleep | [implemented/stub] | [count] |
| Genetic | [implemented/stub] | [count] |

## Infrastructure

- Orientational field: [status]
- LangGraph routing: [status]
- Round-trip calibration: [status]
- Connection matrix: [status]

## Last Directive

[One-line summary of what Directive NNN did]

## Active Blockers

- [List anything that blocks forward progress, or "None"]

## Next Directive Candidates

- [List from DEVLOG "What's Next" section]
```

Populate every field from actual repo inspection — run tests, check which systems are stubs vs implemented, count test files. Do not copy from existing documentation; verify from source.

## Part C: Update CLAUDE.md

Update the project structure section to reflect the new layout:

- Remove `PLANNING_LOG.md` from the root file listing
- Add `planning/` directory with description of its contents
- Explain the two-file pattern: directive + state → DNAgent saves entry + updates CURRENT.md

Update the workflow/collaboration section:

- After completing a directive, DNAgent copies `handoff/state.md` to `planning/NNN_<short_name>.md`
- DNAgent updates `planning/CURRENT.md` from actual repo inspection
- DNAgent reads `planning/CURRENT.md` at the start of every directive for orientation
- `handoff/state.md` is transient — overwritten each cycle by the planning instance

## Part D: Update docs/DIRECTIVES.md

Add a section describing the state file:

- Planning instance provides `handoff/state.md` alongside each directive
- State file contains planning notes: decisions, observations, rationale for this cycle only
- DNAgent copies it to `planning/NNN_<short_name>.md` as a permanent numbered entry
- DNAgent extracts factual state into `CURRENT.md` from actual repo inspection
- `handoff/state.md` is overwritten each cycle; numbered entries are never modified

## Part E: State File for This Directive

The planning instance has placed `handoff/state.md` alongside this directive. Copy it to `planning/006_planning_infrastructure.md` per the new workflow.

The contents of `handoff/state.md` are:

<state_file>
# 006 — Planning Infrastructure Migration

**Date:** 2026-02-08
**Directive type:** Refactoring / Documentation

## Decisions

### Replaced monolithic planning log with entry-based system

The PLANNING_LOG.md was rewritten from scratch four times in five directives. Each rewrite required carrying the full history of rationale forward, and it was growing unmanageably. Migrated to:

- **Numbered entries** (`planning/NNN_*.md`) — one per planning session, never rewritten. Contains decisions, observations, rationale for that cycle.
- **CURRENT.md** — slim factual snapshot maintained by DNAgent from actual repo inspection. Test counts, system status, blockers. Always accurate because it's extracted from ground truth, not manually maintained.

### Division of maintenance responsibility

- Planning instance writes: directive + state (focused planning notes per cycle)
- DNAgent writes: numbered entry (saves the state) + CURRENT.md (extracts factual state from repo)

This solves two problems: the ever-expanding monolith, and the accuracy drift where manually-tracked test counts could diverge from reality.

### Legacy preserved without retrofit

The existing PLANNING_LOG.md becomes `planning/001_through_005_legacy.md`. No attempt to break it into individual entries retroactively. New pattern starts clean from 006.

## Observations

The old planning log served two functions with different update patterns: current-state snapshot (changes every directive, should stay small) and analysis/rationale (accumulates, should never be rewritten). Combining them in one file forced a full rewrite every cycle. Separating them means CURRENT.md stays short and entries accumulate naturally.

## Sequencing Notes

This is the last housekeeping directive before implementation resumes. Directive 007 candidates:

1. **Conscious layer** — first LLM-backed system, semantic domain. Can now integrate with a partially-calibrated orientational field (3 of 4 signal-domain mappings apparatus-confirmed).
2. **Tarka entropy tuning** — refine the modulation strategy so it registers in calibration. Small scope but targeted.
3. **Sleep layer** — transfer function optimization, cache pruning, field weight adjustment. High impact but depends on knowing what "optimized" means.

Leaning toward conscious layer — it's the architectural frontier and will enable semantic validation of the limb-to-feature mappings that are currently only apparatus-confirmed.
</state_file>

## Part F: DEVLOG.md Entry

Append the following entry to the end of `DEVLOG.md`:

```
## 2026-02-08 — Directive 006: Planning Infrastructure Migration

Tests: No change (195 passing)

Migrated from monolithic PLANNING_LOG.md to entry-based planning structure. No code changes.

**New structure:** `planning/` directory with numbered entries (one per planning session, never rewritten) and `CURRENT.md` (factual snapshot maintained by DNAgent from repo inspection).

**New workflow:** Each directive cycle, the planning instance provides a state file alongside the directive. DNAgent saves it as a numbered entry and extracts factual state into CURRENT.md. This replaces the monolithic planning log that was being fully rewritten every cycle.

**Files:** Created `planning/` directory. Moved PLANNING_LOG.md → `planning/001_through_005_legacy.md`. Created `planning/006_planning_infrastructure.md` (first entry in new format). Created `planning/CURRENT.md` (factual snapshot). Updated CLAUDE.md and docs/DIRECTIVES.md to describe new pattern.
```

## Verification Checklist

- [ ] `planning/` directory exists
- [ ] `planning/001_through_005_legacy.md` contains the former PLANNING_LOG.md content
- [ ] `PLANNING_LOG.md` no longer exists at repo root
- [ ] `planning/006_planning_infrastructure.md` copied from `handoff/state.md`
- [ ] `planning/CURRENT.md` created with all fields populated from actual repo inspection
- [ ] CURRENT.md test count matches `pytest` output
- [ ] CURRENT.md system status matches actual source files (not copied from old docs)
- [ ] `CLAUDE.md` updated with new project structure and workflow
- [ ] `docs/DIRECTIVES.md` updated with state file description
- [ ] `DEVLOG.md` has Directive 006 entry appended
- [ ] No code files modified (src/, tests/)
- [ ] All 195 existing tests still pass
- [ ] Git commit and push completed
