# Directive 005 — Housekeeping: Agent Identity, Documentation Accuracy, Planning Log Sync

**Type:** Documentation / Housekeeping
**From:** Planning instance (claude.ai)
**Date:** 2026-02-08

## Context

Directive 004 (motor layer + round-trip calibration) is complete and merged. 195 tests passing. Before moving to the next implementation directive, we need a cleanup pass to:

1. Formalize the build agent's identity as **DNAgent**
2. Sync the planning log with post-Directive 004 analysis
3. Ensure all documentation accurately reflects the current state

This is a zero-code-change directive. No new features, no test changes, no source modifications. Documentation only.

## Read Before Starting

- `CLAUDE.md` — current agent orientation (contains unnamed "Build instance" references)
- `PLANNING_LOG.md` — will be replaced entirely
- `DEVLOG.md` — append new entry
- `handoff/001_response.md` through `handoff/004_response.md` — check for "Transducer Archive" headers

## Part A: Agent Identity — DNAgent

The CLI build agent is now named **DNAgent** (DNA + Agent). The name captures the relationship: agenetic (without origin) is the framework, DNAgent reads genetic instructions (directives) and assembles functional output (code) — like a ribosome reading mRNA and building proteins.

### Changes required:

1. **`CLAUDE.md`** — In the section describing the two-instance collaboration model, replace generic references to "Build instance (Claude Code CLI)" with **DNAgent (Claude Code CLI)**. Add a brief note explaining the name. Do not change the planning instance description (that stays as "Planning instance (claude.ai)").

2. **All `handoff/*_response.md` files** — Replace "Transducer Archive" in the `From:` header line with **DNAgent**. This is a find-and-replace on the header only. Do not modify any other content in these files.

3. **`docs/DIRECTIVES.md`** (if it exists) — Update any references to the build agent to use DNAgent.

## Part B: Replace PLANNING_LOG.md

Replace the entire contents of `PLANNING_LOG.md` with the version provided below. This is the planning instance's authoritative record — it includes post-Directive 004 calibration analysis, the apparatus-vs-hypothesis interpretation caveat, updated limb-to-feature mapping status, and the DNAgent identity decision.

**Do not edit or summarize the replacement content.** Copy it exactly as provided.

<planning_log_replacement>
# Planning Log

Chat-side record of decisions, rationale, and open threads. Updated between directives. Travels with the next directive when the agent needs planning context.

**Last updated: 2026-02-08 (post-Directive 004)**

## Current State

**Completed:** Directives 001–004. Repo scaffolded, signal-domain tier operational (sensory, immune, subconscious), motor layer implemented with round-trip calibration infrastructure. 195 tests passing. Architecture amendment documenting signal-semantics boundary. Documentation and reference material synchronized. Conceptual archaeology synthesis complete. Yoga scroll integration done.

**In progress:** Planning — analyzing calibration results, preparing next directive.

**Queued:** Conscious layer (semantic domain). Sleep layer (weight optimization, cache pruning). Weight system redesign (0.5 midpoint model). Agent identity formalization (DNAgent).

## Active Decisions

### Signal domain implemented as a unit (not one system at a time)

The three signal-domain systems share a processing paradigm: Python-native, no LLM, every-cycle. They also share an interface — the signal report. Implementing them together validated the signal-semantics boundary as an architectural principle rather than just a concept.

### Reference signal = mean of limb weights (v1 simplification)

The orientational field's 18 limb weights (all 1.0) are averaged to produce a single reference value for all signal features. This is deliberately naive.

Consequence: normal text has aggregate_deviation ~2.0 because periodicity/noise/impedance are naturally near 0 while reference is 1.0. Novel input always escalates.

Two planned fixes:
- Sleep optimizes reference values based on actual input distributions (the system learns what "normal" looks like)
- Limb-to-feature mapping — specific limbs correspond to specific signal features instead of uniform mean

Both require experimental validation. Motor round-trip data (Directive 004) provides initial evidence. See "Calibration results" below.

### The 0.5 midpoint weight model (from conceptual archaeology)

Early concept documents specified: "All values are represented as a cycle of 0 to 1 resting at ≈0.5 and summed with a seed value according to a configurable tuning function."

The current implementation uses uniform 1.0 weights. The 0.5 model is more expressive — it allows both amplification (>0.5) and suppression (<0.5) relative to baseline. In signal processing terms, 0.5 is maximum information entropy: the most receptive state. This should be considered for the weight system redesign when sleep is implemented.

### Motor layer as calibration instrument (Directive 004 — COMPLETE)

The motor layer serves dual purpose: it is both the output encoding system AND the experimental apparatus for testing limb-to-feature mappings.

**Biological precedent — reafference:** In embryological development, the sensory and motor systems develop in tandem because the feedback loop between them is the calibration mechanism. A fetus learns proprioception through moving and feeling the result. Neural pathways that fire together wire together. You cannot develop calibrated sensing without producing output and measuring what comes back.

**Implementation:** Motor is a ~460-line signal-level text restructuring engine. Six strategies, each governed by specific limb weights. Deterministic, Python-native, no LLM. Round-trip infrastructure feeds motor output back through sensory and measures feature deltas. Parameterized calibration sweep varies each of 18 limbs individually.

**Motor output representation (RESOLVED):** Text restructuring was chosen — reorder sentences, vary vocabulary, adjust density, add/remove structural markers. Signal feature target vectors and template-based generation were considered but text restructuring provides the most direct round-trip signal for calibration purposes.

### Calibration results and interpretation (NEW — post-Directive 004)

The round-trip calibration sweep produced the following results (limb set to 0.0, all others at baseline 1.0):

| Limb varied | density | entropy | coherence | periodicity | noise_floor | impedance |
|---|---|---|---|---|---|---|
| Prakāśa (0.0) | +0.000 | +0.000 | +0.000 | +0.035 | +0.000 | +0.000 |
| Tarka (0.0) | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| Nivṛtti (0.0) | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.367 |
| Samatvam (0.0) | +0.000 | +0.000 | −0.081 | +0.000 | +0.000 | +0.000 |
| Limbs 4–18 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |

**Confirmed mappings (apparatus level):**
- Prakāśa → periodicity: Suppressing Prakāśa increases periodicity. Motor inserts repeated phrases, sensory measures +0.035 delta.
- Nivṛtti → impedance: Suppressing Nivṛtti increases impedance. Motor adds section markers, sensory measures +0.367 delta. Strongest signal.
- Samatvam → coherence: Suppressing Samatvam decreases coherence. Motor reverses sentence order, sensory measures −0.081 delta.

**Not triggered:**
- Tarka → entropy: The mapping exists in the code but the 30% singleton replacement cap (added to pass repair check after an entropy bug) makes the strategy too conservative to register in the round-trip. The instrument needs tuning for this specific mapping, not a falsification.

**Non-governing limbs (4–18):** Zero response across all features. Changing one limb from 1.0 to 0.0 only shifts the mean from 1.0 to 0.944, insufficient to cross any threshold for mean-governed features (density, noise). This demonstrates genuine selectivity — the system responds specifically to mapped limbs, not uniformly to any weight change.

**CRITICAL INTERPRETATION CAVEAT:** These results confirm the *apparatus works*, not the *hypotheses*. Motor is coded to modulate coherence when Samatvam varies, and the calibration test confirms coherence moves when Samatvam varies. That is a test of the plumbing. The deeper question — does coherence modulation produce output that genuinely embodies "harmonic tone" (the yoga meaning of Samatvam)? — requires the conscious layer to evaluate. We have confirmed the instrument is sensitive and selective. Semantic validation comes later.

### Limb-to-feature mappings are hypotheses, not specifications

The preliminary mapping from conceptual archaeology (Section V) assigns limbs to features across three domains. Current status after Directive 004 calibration:

**Signal domain — apparatus-confirmed:**
- Prakāśa → periodicity (inverse: more Prakāśa = less forced pattern) — ✓ round-trip detectable
- Nivṛtti → impedance (inverse: more Nivṛtti = simpler output) — ✓ round-trip detectable, strongest signal
- Samatvam → coherence (direct: more Samatvam = more coherent) — ✓ round-trip detectable
- Tarka → entropy (direct: more Tarka = more variety) — coded but below detection threshold, needs tuning

**Signal domain — not yet mapped to motor strategies:**
- Māyāvāda → model humility markers (confidence scores, uncertainty flags)
- Ātma-Vichāra → lineage tracking (every output traces to input chain)
- Kṣetra-Jñāna → positional metadata (reports include system state, processing context)

These three are more about what signals *contain* than how text is *restructured*. They may be sensory-side concerns rather than motor-side.

**Semantic domain (planned — requires conscious layer):**
- Tarka → contradiction tracing
- Śraddhā → mystery preservation
- Svadharma → context-appropriate response paths
- Vishvarūpa → threshold pointing

**Meta domain (planned — requires sleep/genetic):**
- Ārēka → hard boundaries (threshold function or continuous weight? — still open)
- Fourfold State → mode tracking (meta-limb governing how other limbs apply? — still open)
- Bodhi → receptive resting state
- No-Position → identity-free processing
- Rest as Realization → graceful shutdown
- Ajāti → echo awareness
- Asparśa → contactless alignment

### The seven-layer provenance is Hermetic, not convergent

The conceptual archaeology revealed that the recurring seven-layer pattern across our systems (MythOS, MiroForge, agenetic framework) traces to a shared root: the Seven Hermetic Principles from the earliest concept documents. The philosophical lineage runs Ra/Thoth/Hermes → Seven Hermetic Principles → Adaptive Coherence Model → Guiding Principles → Asparśa Yoga.

This means the seven-layer convergence is echo from a common ancestor, not independent structural discovery. It doesn't invalidate the architecture (the seven systems are functionally differentiated and each earns its place), but it shifts the "is seven optimal?" question from "evidence suggests yes" to "genuinely open — we need to watch for systems doing double duty or being structurally redundant."

### Yoga implementation needs source material — AVAILABLE

Full implementation source material is assembled:
- Full Asparśa Yoga scrolls (18 limbs, ~2240 lines) at `references/asparsa_yoga_scrolls.md`
- Conceptual archaeology synthesis at `references/conceptual_archaeology.md`
- 18 limb principles at `references/asparsa_limbs.md`

### Build agent identity: DNAgent (NEW)

The CLI build agent's identity is **DNAgent** — DNA + Agent. Lives inside the agenetic (without origin) framework, reads genetic instructions (directives) and assembles functional output (code) — like a ribosome reading mRNA and building proteins.

## Sequencing Rationale

### Why motor before conscious

The original plan was "yoga implementation before conscious" to avoid implementing conscious against a placeholder field. Motor-as-calibration-instrument changes the sequencing:

1. Motor at the signal level doesn't need the conscious layer — it restructures text structurally, not semantically
2. The motor→sensory round-trip provides empirical data for limb-to-feature mapping
3. That mapping data improves the orientational field BEFORE conscious is implemented
4. When conscious finally comes online, it integrates with a field that's been empirically calibrated rather than theoretically specified

This follows biological development order: sensory-motor coupling before higher cognition. The prefrontal cortex (conscious deliberation) is the last brain region to myelinate because it depends on everything below being calibrated first.

### Why signal-level motor is sufficient for calibration

Motor doesn't need to generate meaningful text to test limb-to-feature mappings. It needs to produce output with measurably different signal profiles when different limb weights are active. Signal-level operations (restructuring density, varying vocabulary richness for entropy, reorganizing sentences for coherence) are sufficient. Semantic quality comes later when conscious provides meaning to express.

### Development sequence going forward

Directive 004: Motor layer + round-trip test infrastructure ✓
Directive 005: Cleanup — agent identity, documentation accuracy, planning log sync ✓
→ Directive 006+: Conscious layer (semantic domain) OR Tarka entropy tuning OR sleep layer
→ Sleep layer (needs calibrated field to know what "optimized" means)
→ Weight system redesign (0.5 midpoint, informed by calibration data)

## Open Questions

### Is seven the right number of systems?

The hexagonal packing question from ARCHITECTURE.md. Now informed by the Hermetic provenance discovery — we know the pattern echoes from a shared root rather than emerging independently. Watch for systems doing double duty or structural redundancy as implementation proceeds.

### What constitutes effective sleep consolidation?

The sleep system is the linchpin — it's the only system that writes to genetic expression and the orientational field. What should pruning, strengthening, and reference signal optimization actually look like in practice? Motor calibration data will inform this — sleep needs to know which weights to optimize toward what.

### How minimal can the genetic seed be?

The compression ratio question. Current genetic layer is 18 limbs + principles. Is that the right level of specification, or should it be more/less?

### Cache eviction strategy

Signal pattern cache grows unboundedly. Apoptotic at 10k is a safety valve, not a solution. Sleep needs a real pruning strategy.

### Immune vaccination

Immune log starts empty. Should there be baseline threat patterns seeded from the genetic layer?

### Tarka entropy sensitivity

The entropy modulation strategy is too conservative to register in calibration. The 30% singleton replacement cap (necessary to pass repair check) limits the effect. Options: (a) increase the replacement cap with a more sophisticated repair check, (b) try a different entropy modulation approach (e.g., sentence-level restructuring rather than token replacement), (c) accept that entropy is harder to modulate at the signal level and test Tarka→entropy in the semantic domain instead.

### Apparatus vs hypothesis distinction

The calibration confirms plumbing works but not that yoga semantics map correctly. "Samatvam → coherence" means "adjusting Samatvam weight changes coherence score" — not yet "coherence score captures what Samatvam means." Semantic validation requires conscious layer evaluation. Keep this distinction sharp.

## Threads to Resume

- **Tarka entropy tuning** — refine the modulation strategy or accept it as a semantic-domain test
- **Conscious layer** — first LLM-backed system. Can now integrate with a partially-calibrated orientational field
- **Sleep layer** — transfer function optimization. Blocked on understanding what the orientational field should look like post-calibration
- **Weight system redesign** — move from uniform 1.0 to 0.5 midpoint model. Blocked on sleep + calibration data
- **Semantic validation** — use conscious layer to evaluate whether signal-level restructuring produces output that actually embodies yoga limb semantics
</planning_log_replacement>

## Part C: DEVLOG.md Entry

Append the following entry to the end of `DEVLOG.md`:

```
## 2026-02-08 — Directive 005: Housekeeping — Agent Identity and Documentation Sync

Tests: No change (195 passing)

Cleanup pass. No code changes.

**Agent identity formalized:** The CLI build agent is now **DNAgent** (DNA + Agent). Updated CLAUDE.md and all handoff response headers. The name captures the framework relationship — agenetic (without origin) is the architecture, DNAgent reads genetic instructions (directives) and assembles functional output.

**Planning log replaced:** Full replacement with post-Directive 004 analysis including:
- Calibration results table from round-trip sweep
- Apparatus-vs-hypothesis interpretation caveat (confirmed plumbing works, semantic validation requires conscious layer)
- Updated limb-to-feature mapping status (3 apparatus-confirmed, 1 below threshold, rest pending)
- DNAgent identity decision
- Updated sequencing (Directive 006+ candidates: conscious layer, Tarka tuning, or sleep)

**What changed:** CLAUDE.md (agent name), handoff/*_response.md headers (Transducer Archive → DNAgent), PLANNING_LOG.md (full replacement), DEVLOG.md (this entry).
```

## Part D: Verify No Stale References

After making all changes, search the repo for any remaining instances of:
- "Transducer Archive" — should be zero
- "Build instance" without "DNAgent" context in CLAUDE.md — should be updated
- "pre-Directive 004" — should be zero (old planning log timestamp)

Report any stale references found in the response.

## Verification Checklist

- [ ] All `handoff/*_response.md` files have `From: DNAgent` (not "Transducer Archive")
- [ ] `CLAUDE.md` names the build agent as DNAgent
- [ ] `PLANNING_LOG.md` replaced with provided version (post-Directive 004, includes calibration table)
- [ ] `DEVLOG.md` has Directive 005 entry appended
- [ ] No remaining "Transducer Archive" references anywhere in the repo
- [ ] No code files modified (src/, tests/)
- [ ] All 195 existing tests still pass (run `pytest` to confirm even though no code changed)
- [ ] Git commit and push completed
