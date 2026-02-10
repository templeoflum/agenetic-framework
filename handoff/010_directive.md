# Directive 010 — Audit Remediation

**Type:** Bug Fix / Documentation / Infrastructure
**From:** Planning instance (claude.ai)
**Date:** 2026-02-09

## Context

Directive 009 produced two audit artifacts:
- `handoff/009_audit_report.md` — mechanical audit (DNAgent, raw findings)
- `handoff/009_conceptual_audit.md` — conceptual audit (planning instance, fresh context, adversarial)

The conceptual audit identified 11 findings, triaged into must-fix (4), should-fix (5), and watch (5). This directive addresses all must-fix items and the low-cost should-fix items. It also formalizes the audit protocol so future audits follow the same pattern.

## Read Before Starting

- `handoff/009_conceptual_audit.md` — the full audit with findings and triage table
- `handoff/009_audit_report.md` — mechanical audit (reference for Section 2 state matrix)
- `src/agenetic/systems/sensory.py` — delta computation (Finding 8, the big one)
- `src/agenetic/systems/motor.py` — strategy thresholds and target formulas
- `tests/test_motor.py` — baseline bug (Finding 11)
- `tests/test_round_trip.py` — calibration infrastructure
- `docs/ARCHITECTURE.md` — needs caveat propagation
- `CLAUDE.md` — needs audit protocol section
- `handoff/state.md` — planning notes (copy to `planning/010_audit_remediation.md`)

## Part A: Fix Sensory Delta Computation (Finding 8 — MOST IMPORTANT)

**The problem:** Sensory computes deltas by subtracting the mean of all 18 limb weights (a single scalar) from every feature value. This is dimensionally incoherent — density (~0.8) and entropy (~4.0) are compared against the same reference.

**The fix:** Per-feature reference values derived from the specific limbs that govern each feature. The motor already computes target profiles per-feature in `_compute_target_profile()`. Sensory should use the same mapping to compute per-feature references.

Implementation approach:

```python
# Instead of:
reference = mean_of_all_limb_weights
density_delta = features["density"] - reference

# Do:
density_ref = _feature_reference(limbs, "density")    # uses mean weight, same as motor target
entropy_ref = _feature_reference(limbs, "entropy")     # uses Tarka weight
coherence_ref = _feature_reference(limbs, "coherence") # uses Samatvam weight
periodicity_ref = _feature_reference(limbs, "periodicity")  # uses Prakāśa weight
noise_ref = _feature_reference(limbs, "noise_floor")   # uses Śraddhā weight
impedance_ref = _feature_reference(limbs, "impedance") # uses Nivṛtti weight
```

The reference formulas should match the motor's target profile formulas from Directive 008:

| Feature | Reference formula | At 0.5 baseline |
|---|---|---|
| density | `0.8 + (mean_w - 0.5) * 0.4` | 0.8 |
| entropy | `3.5 + (tarka_w - 0.5) * 3.0` | 3.5 |
| coherence | `0.35 + (samatvam_w - 0.5) * 0.7` | 0.35 |
| periodicity | `(0.5 - prakasa_w) * 0.6` | 0.0 |
| noise_floor | `(0.5 - sraddha_w) * 0.6` | 0.0 |
| impedance | `(0.5 - nivrtti_w) * 0.6` | 0.0 |

This means sensory and motor share the same understanding of what "expected" looks like for a given field state. The delta is now: "how far is this feature from what the field expects" — which is what the architecture always intended.

**Important:** This is a shared computation. Rather than duplicating formulas in motor and sensory, extract the target profile computation into a shared utility (e.g., `src/agenetic/utils/target_profile.py` or a function in `base.py`) that both systems import. This eliminates the risk of the formulas drifting apart.

**Impact:** This changes delta values for every signal report, which affects:
- `aggregate_deviation` computation
- Immune threat classification thresholds
- Subconscious escalation priming thresholds
- All calibration data

Review all downstream thresholds after the change. The calibration sweep will need to re-run, and existing threshold values in immune and subconscious may need adjustment. Don't guess — run the tests, see what breaks, adjust based on actual values.

## Part B: Fix test_motor.py Baseline (Finding 11)

In `tests/test_motor.py`, change `_vary_single_limb(limb_id, weight, baseline=1.0)` to `baseline=0.5`.

Then run the full test suite. Fix any test expectations that break due to the baseline change. As with Directive 008: no tests removed, only expectations adjusted.

## Part C: Document Tautological Calibration Pattern (Finding 4)

The audit identified a systematic property: strategies that share mechanism with their measurement (motor bridges words between sentences, sensory measures word overlap between sentences) produce guaranteed confirmation. The one strategy that attempts genuine cross-level measurement (Tarka: rearranges sentences, measures token-frequency entropy) fails.

Add a section to `docs/ARCHITECTURE.md` titled "Calibration Validity" or similar, that states:

1. The calibration framework validates **plumbing** — that motor strategies produce measurable changes in sensory features.
2. Strategies whose transformation mechanism directly overlaps with their measurement mechanism (e.g., coherence: word bridging measured by word overlap) produce guaranteed confirmation. These are **verified connections**, not empirical discoveries.
3. Tarka's failure to register is the most informative calibration result: it demonstrates that strategies operating on a different level of text than their measurement do not produce guaranteed confirmation. This is evidence that the calibration framework can discriminate.
4. True validation of limb-to-feature mappings requires the conscious layer, which can evaluate whether signal-level modulations produce meaningful behavioral differences.

## Part D: Propagate Engineering Assignment Caveat (Finding 2)

The planning documents (007, 008) carry honest caveats about the limb-to-feature mappings being engineering assignments, not philosophical derivations. These caveats don't appear in ARCHITECTURE.md, the code, or test docstrings.

Add to `docs/ARCHITECTURE.md` in the limb mapping section:

> The mapping from yoga limbs to signal features is an engineering assignment, not a philosophical derivation. Prakāśa governs periodicity in the motor because periodicity needed a governing limb and Prakāśa's description ("perceive without possession") was interpreted as cyclical perception. Other mappings were equally plausible. The conscious layer is free to interpret limb meanings differently at the semantic level than the motor encodes them at the signal level. Signal-level mappings are transfer function coefficients, not truth claims about what the limbs mean.

Also: replace the word "confirmed" with "verified" in DEVLOG.md entries and README.md when referring to calibration results. Use "apparatus-verified" or "verified connection" instead of "apparatus-confirmed" or "confirmed mapping."

## Part E: Rename Calibration Language (Finding 1)

Search all documentation files (DEVLOG.md, README.md, planning entries) for "confirmed mapping" / "apparatus-confirmed" and replace with "verified connection" / "apparatus-verified." This is a documentation-only change — no code or test modifications.

## Part F: Expand Calibration Inputs (Finding 9)

The calibration sweep uses a single input text (4 sentences of clean structured prose). Strategy behavior is input-dependent — Ārēka only fires on noisy input, asymmetry reflects input characteristics, not strategy characteristics.

Add 2-4 additional calibration inputs to `tests/test_round_trip.py`:

```python
CALIBRATION_INPUTS = {
    "clean_prose": "The quick brown fox jumps over the lazy dog. ...",  # existing
    "noisy_text": "Th3 qu!ck br0wn f0x... ||marker|| ...#@$...",  # high noise, high impedance
    "short_input": "Hello world.",  # minimal text
    "code_like": "def process(state): return {**state, 'output': transform(state['input'])}",  # structural
    "long_repetitive": "..." # longer text with natural repetition patterns
}
```

Run the full sweep for each input type. The summary test should print a table per input type, or a combined table with an input column. The goal is to characterize the **response surface** — how each strategy behaves across input types — not just one operating point.

This is the directive's largest test infrastructure change. If it makes the test suite significantly slower, consider marking the multi-input sweep as a separate test class that can be run independently (e.g., `pytest -k "calibration_surface"` vs the regular suite).

## Part G: Tarka Entropy Measurement (Finding 4 — Should Fix)

The audit suggests character-level or bigram entropy would respond to sentence splitting/merging (which changes character distribution and bigram patterns even when vocabulary is preserved).

Add an alternative entropy measurement to sensory. Don't replace the existing token-frequency entropy — add a second measurement. Options:

1. **Character bigram entropy:** Shannon entropy over character bigram frequency distribution. Sentence splitting changes punctuation, capitalization, and whitespace patterns, which changes bigram frequencies.
2. **Sentence length variance:** Not entropy per se, but a measure of structural diversity. Sentence splitting/merging directly changes this.

Add whichever is simpler as `structural_entropy` or `bigram_entropy` to SignalFeatures. Keep the existing `entropy` field. Then check whether Tarka's sentence-level strategy produces a measurable delta in the new measurement.

If it does: we've found a measurement that matches the strategy's mechanism. Document this as another "verified connection" (not confirmed — same tautological pattern, but at least the connection works).

If it doesn't: Tarka is genuinely semantic-domain. Document accordingly and move on.

**Important:** Adding a feature to SignalFeatures means updating sensory, base.py types, and any code that reads signal features. Check all consumers.

## Part H: Audit Protocol in CLAUDE.md

Add a section to `CLAUDE.md` documenting the audit protocol as a repeatable process:

```markdown
## Audit Protocol

Audits are triggered before major architectural transitions (e.g., before implementing a new domain tier). They produce two artifacts, both prefixed with the directive number that triggered them:

1. **Mechanical audit** (`NNN_audit_report.md`): Produced by DNAgent via a zero-code-change directive. Reads every file, reports raw findings across a standard checklist (interface compliance, state flow, type consistency, test coverage, dead code, documentation accuracy). No interpretation.

2. **Conceptual audit** (`NNN_conceptual_audit.md`): Produced by the planning instance in a fresh chat (clean context, no inherited assumptions). Reads the mechanical audit plus key source files. Evaluates architectural soundness, circular reasoning, self-fulfilling prophecies, logical gaps. Adversarial posture.

Findings are triaged into:
- **Must fix:** Blocks the next phase
- **Should fix:** Improves quality, not blocking
- **Watch:** Monitor during next phase

A remediation directive follows, addressing must-fix items and low-cost should-fix items.
```

## Part I: DEVLOG and Planning Updates

- **`DEVLOG.md`:** Append Directive 010 entry summarizing: audit findings addressed, delta computation fix, calibration language correction, multi-input calibration, Tarka bigram entropy experiment. Include the updated calibration table from the multi-input sweep.
- **`planning/CURRENT.md`:** Update from repo inspection after all changes.
- **`README.md`:** Update test count, any description changes.
- Copy `handoff/state.md` to `planning/010_audit_remediation.md`.

## Verification Checklist

- [ ] `handoff/state.md` copied to `planning/010_audit_remediation.md`
- [ ] **Sensory delta uses per-feature references** (not global mean)
- [ ] Target profile formulas extracted to shared utility (motor and sensory import the same function)
- [ ] Downstream thresholds (immune, subconscious) reviewed and adjusted if needed
- [ ] `test_motor.py` baseline changed from 1.0 to 0.5
- [ ] No tests removed — only expectations adjusted
- [ ] Calibration validity section added to ARCHITECTURE.md
- [ ] Engineering assignment caveat added to ARCHITECTURE.md
- [ ] "confirmed" → "verified" across all documentation
- [ ] 3-5 calibration input types added to test_round_trip.py
- [ ] Multi-input calibration sweep runs and prints results
- [ ] Bigram entropy (or character-level) measurement added to sensory
- [ ] SignalFeatures updated in base.py for new measurement
- [ ] Tarka tested against new measurement — result documented either way
- [ ] Audit protocol section added to CLAUDE.md
- [ ] All tests pass
- [ ] `planning/CURRENT.md` updated from repo inspection
- [ ] `DEVLOG.md` has Directive 010 entry with calibration tables
- [ ] `README.md` updated
- [ ] Git commit and push completed
