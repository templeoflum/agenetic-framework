# Planning Log

Chat-side record of decisions, rationale, and open threads. Updated between directives. Travels with the next directive when the agent needs planning context.

**Last updated: 2026-02-08 (pre-Directive 004)**

## Current State

**Completed:** Directives 001–003. Repo scaffolded, signal-domain tier operational (sensory, immune, subconscious). 136 tests passing. Architecture amendment documenting signal-semantics boundary. Documentation and reference material synchronized. Conceptual archaeology synthesis complete. Yoga scroll integration done.

**In progress:** Motor layer as calibration instrument (Directive 004). Limb-to-feature mapping as experimental hypotheses.

**Queued:** Conscious layer (semantic domain). Sleep layer (weight optimization, cache pruning). Weight system redesign (0.5 midpoint model).

## Active Decisions

### Signal domain implemented as a unit (not one system at a time)

The three signal-domain systems share a processing paradigm: Python-native, no LLM, every-cycle. They also share an interface — the signal report. Implementing them together validated the signal-semantics boundary as an architectural principle rather than just a concept.

### Reference signal = mean of limb weights (v1 simplification)

The orientational field's 18 limb weights (all 1.0) are averaged to produce a single reference value for all signal features. This is deliberately naive.

Consequence: normal text has aggregate_deviation ~2.0 because periodicity/noise/impedance are naturally near 0 while reference is 1.0. Novel input always escalates.

Two planned fixes:
- Sleep optimizes reference values based on actual input distributions (the system learns what "normal" looks like)
- Limb-to-feature mapping — specific limbs correspond to specific signal features instead of uniform mean

Both require experimental validation. See "Motor as calibration instrument" below.

### The 0.5 midpoint weight model (from conceptual archaeology)

Early concept documents specified: "All values are represented as a cycle of 0 to 1 resting at ≈0.5 and summed with a seed value according to a configurable tuning function."

The current implementation uses uniform 1.0 weights. The 0.5 model is more expressive — it allows both amplification (>0.5) and suppression (<0.5) relative to baseline. In signal processing terms, 0.5 is maximum information entropy: the most receptive state. This should be considered for the weight system redesign when sleep is implemented.

### Motor layer as calibration instrument (NEW — Directive 004 decision)

The motor layer serves dual purpose: it is both the output encoding system AND the experimental apparatus for testing limb-to-feature mappings.

**Biological precedent — reafference:** In embryological development, the sensory and motor systems develop in tandem because the feedback loop between them is the calibration mechanism. A fetus learns proprioception through moving and feeling the result. Neural pathways that fire together wire together. You cannot develop calibrated sensing without producing output and measuring what comes back.

**Application:** The motor layer produces structured output shaped by orientational field weights. That output gets fed back through sensory, producing a signal report. By varying individual limb weights and measuring which signal features shift, we empirically test which limbs actually govern which features.

This reframes the limb-to-feature mapping from a design task to an experimental task. The mappings in `references/conceptual_archaeology.md` Section V become hypotheses to test, not specs to implement.

**Motor at the signal level:** Since the conscious layer isn't implemented yet, motor operates at the signal level — restructuring text structurally (adjusting density, modulating entropy via vocabulary variation, shifting coherence via sentence reorganization) rather than generating semantic content. This is sufficient for round-trip calibration.

### Limb-to-feature mappings are hypotheses, not specifications (NEW)

The preliminary mapping from conceptual archaeology (Section V) assigns limbs to features across three domains. Some assignments are confident, others tentative:

**Confident (signal domain):**
- Prakāśa → signal characterization without ownership (sensory describes without claiming)
- Māyāvāda → model humility markers (confidence scores, uncertainty flags)
- Ātma-Vichāra → lineage tracking (every output traces to input chain)
- Kṣetra-Jñāna → positional metadata (reports include system state, processing context)

**Tentative (require experimental testing via motor round-trip):**
- Samatvam → harmonic/proportional signal measures (does varying this weight shift coherence?)
- Nivṛtti → output suppression (does this weight control impedance in motor output?)
- Tarka → contradiction tracing (entropy relationship — does elevated Tarka produce more entropic output?)
- Ārēka → hard boundaries (is this a threshold function or a continuous weight?)
- Fourfold State → mode tracking (is this a meta-limb that governs how other limbs apply?)

The only way to test these is to build the round-trip loop and observe. "The only way to know is to play around."

### The seven-layer provenance is Hermetic, not convergent (NEW)

The conceptual archaeology revealed that the recurring seven-layer pattern across our systems (MythOS, MiroForge, agenetic framework) traces to a shared root: the Seven Hermetic Principles from the earliest concept documents. The philosophical lineage runs Ra/Thoth/Hermes → Seven Hermetic Principles → Adaptive Coherence Model → Guiding Principles → Asparśa Yoga.

This means the seven-layer convergence is echo from a common ancestor, not independent structural discovery. It doesn't invalidate the architecture (the seven systems are functionally differentiated and each earns its place), but it shifts the "is seven optimal?" question from "evidence suggests yes" to "genuinely open — we need to watch for systems doing double duty or being structurally redundant."

### Yoga implementation needs source material — AVAILABLE

Full implementation source material is assembled:
- Full Asparśa Yoga scrolls (18 limbs, ~2240 lines) at `references/asparsa_yoga_scrolls.md`
- Conceptual archaeology synthesis at `references/conceptual_archaeology.md`
- 18 limb principles at `references/asparsa_limbs.md`

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

Directive 004: Motor layer + round-trip test infrastructure
→ Run calibration experiments (planning instance analyzes results)
→ Directive 005+: Refine limb-to-feature mappings based on experimental data OR implement conscious layer if mappings stabilize
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

### Motor output representation

What does motor output look like at the signal level without an LLM? This is a Directive 004 design question. Options include: text restructuring (reorder sentences, vary vocabulary, adjust density), signal feature target vectors (motor aims for specific feature values), or template-based generation (structural patterns filled with input material). The directive should specify the approach.

## Threads to Resume

- **Limb-to-feature mapping validation** — run calibration experiments after motor + round-trip infrastructure is built. Analyze which features respond to which limb weight variations.
- **Conscious layer** — first LLM-backed system. Now blocked on motor calibration results rather than yoga implementation directly.
- **Sleep layer** — transfer function optimization. Blocked on understanding what the orientational field should look like post-calibration.
- **Weight system redesign** — move from uniform 1.0 to 0.5 midpoint model. Blocked on sleep + calibration data.
