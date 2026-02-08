# Directive 003 — Documentation and Reference Material Synchronization

**From:** Planning instance (claude.ai)
**To:** Transducer Archive (CLI agent)
**Date:** 2026-02-08

## Context

After Directives 001 (scaffold) and 002 (signal-domain tier), multiple planning sessions produced documentation and reference material. Some files were drafted and placed locally but never committed. Two new reference documents were created during a conceptual archaeology review of the project's source material. This directive synchronizes the repo.

**Read `PLANNING_LOG.md` at the repo root first** — it contains full context on all active decisions, sequencing rationale, and open questions. It has been updated with outcomes from the conceptual archaeology work.

## Objective

Ensure every file produced during planning sessions is present, consistent, and committed. Update CLAUDE.md to reflect the current project structure. No code changes.

## Part A: Verify Core Documentation

The following files should already exist at the repo root. Verify each is present and non-empty. If any are missing, flag it in the response — do NOT create them.

### A1: Verify files exist
- `README.md` — should describe the project, seven systems, signal-semantics boundary, current status, project structure. If it still contains the original stub from Directive 001 (starts with "The Agenetic Framework" and has a "Core Idea" section), flag it as needing replacement.
- `DEVLOG.md` — chronological build log. Should have entries for Directive 001, architecture amendment, and Directive 002.
- `PLANNING_LOG.md` — should have "Last updated: 2026-02-08" near the top and sections on conceptual archaeology outcomes.

## Part B: Verify Reference Material

### B1: Verify reference files exist
- `references/asparsa_limbs.md` — the original 18 limb principles from Directive 001. Should already be present.
- `references/asparsa_yoga_scrolls.md` — full yoga source text (~2240 lines, 18 limbs with extended definitions and Ritual Practice questions). Should be pre-placed by user.
- `references/conceptual_archaeology.md` — synthesis document mapping patterns from earlier concept documents to current architecture. Contains sections on philosophical lineage, recurring structural patterns, Hermetic-to-Yogic pivot, and preliminary limb-to-feature mapping. Should be pre-placed by user.

If any reference files are missing, flag them in the response with the expected filename.

## Part C: Update CLAUDE.md

### C1: Update project structure in CLAUDE.md

The project structure section in CLAUDE.md needs to reflect all current files. Update it to include:

```
agenetic-framework/
├── DEVLOG.md                        # What was built and why (repo memory)
├── PLANNING_LOG.md                  # Decisions, rationale, open threads (chat memory)
├── CLAUDE.md                        # Agent orientation (this file)
├── README.md                        # Project description and status
├── pyproject.toml                   # Python project config
├── docs/
│   ├── ARCHITECTURE.md              # Full v2 framework specification
│   ├── DIRECTIVES.md                # How the directive system works
│   ├── architecture_amendment.md    # Signal-semantics boundary
│   └── signal_report_structure.md   # Signal report TypedDict spec
├── handoff/                         # Directive/response exchange files
├── references/
│   ├── asparsa_limbs.md             # 18 limb principles (genetic seed)
│   ├── asparsa_yoga_scrolls.md      # Full yoga source text (~2240 lines)
│   └── conceptual_archaeology.md    # Pattern extraction from concept docs
├── src/agenetic/
│   ├── systems/                     # The seven systems
│   ├── network/                     # Topology, connections, routing
│   ├── field/                       # Orientational field
│   └── regulation/                  # Homeostasis, repair, apoptosis
└── tests/
```

### C2: Add reference material context to CLAUDE.md

Add the following section to CLAUDE.md after the project structure, if no similar section exists:

```markdown
## Reference Material

The `references/` directory contains source material that informs architecture decisions:

- **asparsa_limbs.md** — The 18 limb principles as encoded in the genetic seed. These are the one-line definitions used in `orientational.py`.
- **asparsa_yoga_scrolls.md** — The full canonical source text for the Asparśa Yoga practice. Contains extended definitions, behavioral implications, and Ritual Practice questions for each limb. This is the authoritative source for limb-to-feature mapping work.
- **conceptual_archaeology.md** — Synthesis of 8 earlier concept documents tracing the project's philosophical lineage from Hermetic principles through to the current Yogic framework. Contains preliminary limb-to-feature mapping across signal/semantic/meta domains. Treat mappings as hypotheses to be tested, not specifications to be implemented.
```

## Part D: DEVLOG Entry

### D1: Add entry to DEVLOG.md

Append the following entry to DEVLOG.md:

```markdown
---

## 2026-02-08 — Directive 003: Documentation and Reference Material Sync

**Tests:** No change (136 passing)

Housekeeping pass. Synchronized all documentation and reference material produced during planning sessions:

- Verified README.md, DEVLOG.md, PLANNING_LOG.md present at repo root
- Added yoga scrolls and conceptual archaeology synthesis to `references/`
- Updated CLAUDE.md project structure and added reference material context
- No code changes

This directive clears the documentation backlog so future directives operate against an accurate repo state.
```

## Scope Boundaries

**DO:**
- Verify all listed files exist and are non-empty
- Update CLAUDE.md project structure and add reference material section
- Append DEVLOG entry
- Flag any missing files in the response
- Git commit and push

**DO NOT:**
- Create missing documentation files (README, DEVLOG, PLANNING_LOG) — flag them instead
- Modify any source code
- Modify any existing reference files
- Edit historical handoff files (001_*, 002_*)
- Run tests (no code changes to validate)

## Deliverables

| File | Action |
|------|--------|
| `CLAUDE.md` | Updated (project structure + reference material section) |
| `DEVLOG.md` | Updated (new entry appended) |
| `handoff/003_directive.md` | This file |
| `handoff/003_response.md` | Agent's completion report |

## Verification Checklist

- [ ] README.md exists and is not the Directive 001 stub
- [ ] DEVLOG.md exists with entries for Directives 001, 002, and 003
- [ ] PLANNING_LOG.md exists with "Last updated: 2026-02-08"
- [ ] `references/asparsa_limbs.md` exists (from Directive 001)
- [ ] `references/asparsa_yoga_scrolls.md` exists (~2240 lines)
- [ ] `references/conceptual_archaeology.md` exists (has "Philosophical Lineage" section)
- [ ] CLAUDE.md project structure includes all files listed above
- [ ] CLAUDE.md has reference material context section
- [ ] No source code files modified
- [ ] No historical handoff files edited
- [ ] Git commit and push completed
