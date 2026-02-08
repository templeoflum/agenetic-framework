# Directive System

## Overview

This project uses directive-based collaboration between two Claude instances. The **planning instance** (claude.ai chat) handles architecture decisions, design thinking, and review. **DNAgent** (Claude Code CLI) handles implementation, testing, and reporting.

The `handoff/` directory is the interface between them. All coordination passes through numbered directive and response files.

## Why Directives

Every CLI session is a cold start. DNAgent has no memory of previous conversations, planning discussions, or design rationale beyond what exists in the repo itself. Directives solve this by packaging everything the agent needs into a single self-contained document.

This also creates an automatic project history. The sequence of directives and responses is the narrative of how the system was built.

## Directive Structure

```markdown
# Directive NNN — [Descriptive Title]

**Date:** [YYYY-MM-DD]

## Context

Why this directive exists. What was decided, what changed, what the
build instance needs to understand to execute correctly. Include enough
background that DNAgent with zero conversation history can act
on this alone.

Reference specific files in the repo when relevant:
"See docs/ARCHITECTURE.md, Section: Network Topology"

## Objective

1–3 sentences. What needs to happen. State scope clearly — whether this
involves new code, modifications to existing code, research, or
structural changes.

## Tasks

### Task 1: [Specific Action]

Precise instructions. If creating files, specify paths. If implementing
a system, specify interfaces and expected behavior. If there are design
decisions that are already made, state them — don't leave them open for
the build instance to re-decide.

### Task 2: [Next Action]
...

## Scope Boundaries

**DO:**
- [Explicit list of what the agent should do]

**DO NOT:**
- [Explicit list of what the agent must not do]
- Do not modify historical handoff files
- Do not make architecture decisions not covered in this directive

## Deliverables

| File/Path | Action | Description |
|-----------|--------|-------------|
| `src/agenetic/systems/sensory.py` | Create | Sensory layer implementation |
| `tests/test_sensory.py` | Create | Tests for sensory layer |
| `handoff/NNN_response.md` | Create | Completion report |

## Verification Checklist

- [ ] [Each deliverable gets a checkable item]
- [ ] [Be specific — "sensory node accepts dict input and returns dict" not "sensory works"]
- [ ] All tests pass
- [ ] No files outside scope modified
- [ ] No historical handoff files edited
- [ ] Git commit with descriptive message
```

## Key Principles

**Self-containment.** No "as we discussed" or "per the previous directive." If context matters, include it inline. The build instance shouldn't need to read previous directives to execute the current one (though it can reference them for historical context).

**Explicit design decisions.** If the planning instance has already decided something — an interface, a data structure, a naming convention — state it in the directive. Don't leave settled questions open for DNAgent to re-decide.

**Scope boundaries are mandatory.** The DO NOT list prevents scope creep. DNAgent should treat anything not explicitly in scope as out of scope.

**Honest reporting.** The response file should document what actually happened, including failures, surprises, and open questions. The planning instance needs ground truth, not a success narrative.

**One directive, one coherent unit of work.** Each directive should represent a single phase, feature, or task that can be completed, tested, and committed as a unit. If a directive is getting too large, it probably wants to be two directives.

## Response Structure

```markdown
# Response NNN — [Same Title as Directive]

**Date:** [YYYY-MM-DD]

## Summary

What was done, in 2–3 sentences.

## Completed Tasks

### Task 1: [Title]
What was implemented, any decisions made within scope, any deviations
from the directive and why.

### Task 2: [Title]
...

## Verification Checklist

- [x] [Completed items]
- [ ] [Incomplete items with explanation]

## Test Results

```
[paste test output]
```

## Issues & Open Questions

Anything the planning instance should know about. Problems encountered,
design questions that surfaced during implementation, things that worked
differently than expected.

## Files Changed

| File | Action | Notes |
|------|--------|-------|
| `src/agenetic/systems/sensory.py` | Created | ... |
```

## Numbering

Directives are numbered sequentially: 001, 002, 003, etc. Responses share the same number as their directive. No gaps in numbering. If a directive is abandoned before completion, the response should note this.
