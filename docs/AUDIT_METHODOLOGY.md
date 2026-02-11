# Audit Methodology

## Lessons Learned (D009/D015 → D010/D016)

The project's first two audit cycles (D009/D015 mechanical + conceptual audits, D010/D016 remediation) revealed a structural problem with how audit findings were organized and addressed.

### The Problem: Severity-First Organization Causes Phase Drift

Both audits presented findings as flat severity-ranked lists: critical findings first, recommendations last. Remediation directives followed this ordering — fixing the most severe issues regardless of which architectural phase they belonged to.

The result: D010 remediated per-feature delta (Phase 1 fix) alongside calibration infrastructure (Phase 2 work) in a single directive. D016 remediated cache pruning (Phase 1 fix), escalation flag preservation (Phase 1 fix), immune escalation (Phase 1 fix), and feature normalization (Phase 1 fix) — but the cache pruning was described in Phase 3 terms (self-regulation). D017 implemented sleep with weight modification (Phase 2 scheduling + Phase 3 adaptive behavior) in one directive.

By D017, the project had partially implemented Phases 1, 2, and 3 with no phase cleanly complete.

### The Fix: Phase-First, Severity-Second

Future audits must:

1. **Classify every finding by phase** — which phase does this finding belong to? If a finding spans phases, document the dependency.

2. **Present findings grouped by phase** — within each phase group, order by severity. This makes it visible when a high-severity finding would pull remediation into a different phase.

3. **Remediation directives stay within one phase** — unless a finding is a deployment hazard (like the 10K cache time bomb). Cross-phase remediation requires explicit justification in the directive and must be tracked in CURRENT.md's phase completion section.

4. **CURRENT.md tracks phase items** — each directive documents which phase items it closes. The planning instance reviews phase completion state before scoping the next directive.

### Audit Structure Template

```
## Phase 1 Findings
### Critical
### Important
### Informational

## Phase 2 Findings
### Critical
### Important
### Informational

## Phase 3 Findings
[...]

## Cross-Phase Findings
[Findings that span multiple phases, with dependency analysis]
```
