# 008 — Midpoint Weight Migration and Recalibration

**Date:** 2026-02-08
**Directive type:** Refactoring / Calibration

## Decisions

### Midpoint migration was blocked on a phantom dependency

The planning log listed the 0.5 midpoint weight model as "blocked on sleep + calibration data." The calibration data blocker cleared after Directive 004, but sleep was never a real blocker — default weights are a genetic/field concern (factory calibration), not a sleep concern (runtime optimization). Sleep optimizes weights during operation; genetic sets the starting position. Neither needs to exist to change the default.

We had two rounds of calibration data (Directives 004 and 007) against a baseline we knew was wrong. The data validated plumbing and strategies but the mapping landscape may look different at 0.5. This should have been caught earlier — lesson for future planning: audit blocker lists when their stated dependencies get resolved.

### 0.5 as maximum information entropy

The midpoint isn't arbitrary. In signal processing terms, 0.5 on a 0-to-1 scale is the point of maximum information entropy — the most receptive state, equally capable of moving in either direction. At 1.0, every limb is maxed out with nowhere to go but down. At 0.5, the system can amplify OR suppress any limb, and the resting state represents genuine openness rather than saturation.

This also aligns with the yoga: the default state should be receptive (Prakāśa as open perception), not maximally active.

### Symmetric formulas may be cleaner

The existing target formulas were designed for 1.0 defaults and include a mix of direct (`weight * scale`) and inverse (`(1.0 - weight) * scale`) relationships. At 0.5 these should ideally be symmetric: `target = base + (weight - 0.5) * scale`. Whether DNAgent adopts this or uses simpler adjustments is left to implementation judgment — the directive specifies the design principle, not the formula.

### Three-point sweep replaces two-point

Previous sweeps tested 0.0 and 0.5. With 0.5 as the new baseline, the sweep tests 0.0 (full suppression), 0.5 (baseline, should be near-zero delta), and 1.0 (full amplification). This gives the full response curve and tells us whether mappings are symmetric around the midpoint.

### The "everything escalates" problem may partially resolve

At 1.0 reference, typical text had aggregate_deviation ~2.0 because periodicity/noise/impedance are naturally near 0 while the reference was 1.0. At 0.5 reference, the gap shrinks. This was a known issue since Directive 002 (novel input always escalates) with "sleep optimizes reference" as the planned fix. Midpoint migration may be the simpler fix — or at least reduce the severity.

## Observations

This directive is the first that changes the operating conditions of already-working systems. Previous directives built new things; this one changes the ground under existing things. That means test breakage is expected and the fix-vs-remove discipline matters. Weakening tests to pass is not allowed — only adjusting expectations to match correct new behavior.

The binary-vs-graded finding from Directive 007 (only Samatvam showed proportional response) might be an artifact of the 1.0 baseline. At 0.5, the symmetric formula structure should produce proportional responses by construction. If mappings are still binary at 0.5, that's a real finding about threshold effects rather than a baseline artifact.

## Sequencing Notes

After 008, all signal-domain and motor calibration is against the intended operating point. The data should be stable enough to inform conscious layer design.

Directive 009 candidates:
1. **Conscious layer** — we now have clean calibration data against the correct baseline, convergent cluster analysis showing what conscious needs to differentiate, and 9 motor strategies providing the output mechanism. The architectural frontier.
2. **Tarka deep dive** — two approaches have failed to register entropy changes in calibration. Worth one more attempt or accept as semantic-domain.
3. **Ātma-Vichāra analysis** — the one uncategorized limb. Lineage tracking may be a cross-cutting concern rather than a feature modulation.

Strong lean toward conscious layer. The signal domain has been thoroughly explored and its limits are well-characterized.
