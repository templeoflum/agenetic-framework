# 006 — Planning Infrastructure Migration

**Date:** 2026-02-08
**Directive type:** Refactoring / Documentation

## Decisions

### Replaced monolithic planning log with entry-based system

The PLANNING_LOG.md was rewritten from scratch four times in five directives. Each rewrite required carrying the full history of rationale forward, and it was growing unmanageably. Migrated to:

- **Numbered entries** (`planning/NNN_*.md`) — one per planning session, never rewritten. Contains decisions, observations, rationale for that cycle.
- **CURRENT.md** — slim factual snapshot maintained by DNAgent from actual repo inspection. Test counts, system status, blockers. Always accurate because it's extracted from ground truth, not manually maintained.

### Division of maintenance responsibility

- Planning instance writes: directive + state (focused planning notes per cycle), both dropped in `handoff/`
- DNAgent writes: numbered entry (copies state.md to planning/NNN_*.md) + CURRENT.md (extracts factual state from repo)

This solves two problems: the ever-expanding monolith, and the accuracy drift where manually-tracked test counts could diverge from reality.

### handoff/state.md is transient

`state.md` always lives in `handoff/` and gets overwritten each cycle. It's an exchange document, not a permanent record. DNAgent copies it to the numbered entry before it gets overwritten next cycle.

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
