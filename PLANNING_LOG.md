# Planning Log

Chat-side record of decisions, rationale, and open threads. Updated between directives. Travels with the next directive when the agent needs planning context.

Last updated: 2026-02-08

---

## Current State

**Completed:** Directives 001–002. Repo scaffolded, signal-domain tier operational (sensory, immune, subconscious). 136 tests passing. Architecture amendment documenting signal-semantics boundary.

**In progress:** Documentation and reference material synchronization (Directive 003). Yoga scroll integration. Conceptual archaeology synthesis complete.

**Queued:** Limb-to-feature mapping (encoding yoga limbs as system behaviors). Conscious layer (semantic domain). Sleep layer (weight optimization, cache pruning).

## Active Decisions

### Signal domain implemented as a unit (not one system at a time)
The three signal-domain systems share a processing paradigm: Python-native, no LLM, every-cycle. They also share an interface — the signal report. Implementing them together validated the signal-semantics boundary as an architectural principle rather than just a concept.

### Reference signal = mean of limb weights (v1 simplification)
The orientational field's 18 limb weights (all 1.0) are averaged to produce a single reference value for all signal features. This is deliberately naive. Consequence: normal text has aggregate_deviation ~2.0 because periodicity/noise/impedance are naturally near 0 while reference is 1.0. Novel input always escalates.

**Two planned fixes:**
1. Sleep optimizes reference values based on actual input distributions (the system learns what "normal" looks like)
2. Limb-to-feature mapping — specific limbs correspond to specific signal features (Tarka → entropy, Nivṛtti → impedance, etc.) instead of uniform mean

Both require the yoga implementation to be fleshed out first — we need to know what each limb actually governs before we can map them to signal features.

### The 0.5 midpoint weight model (NEW — from conceptual archaeology)
Early concept documents specified: "All values are represented as a cycle of 0 to 1 resting at ≈0.5 and summed with a seed value according to a configurable tuning function." The current implementation uses uniform 1.0 weights. The 0.5 model is more expressive — it allows both amplification (>0.5) and suppression (<0.5) relative to baseline. In signal processing terms, 0.5 is maximum information entropy: the most receptive state. This should be considered for the weight system redesign when sleep is implemented.

### Yoga implementation needs source material — NOW AVAILABLE
What's in `orientational.py` is the ARCHITECTURE.md extraction: 18 one-line principles, uniform weight 1.0. The actual practice is much richer. Full implementation needs:
- Operational behavioral profiles per limb (not just principle statements)
- Contextual activation patterns (when does each limb activate)
- Sensitivity profiles (which signal features each limb responds to)
- Inter-limb relationships (reinforcement, tension-checking)
- The Fourfold State Map (Limb XVI) as a meta-structure governing how other limbs apply across modes

**Source material now assembled:**
- Full Asparśa Yoga scrolls (18 limbs, ~2240 lines) — canonical source text with Ritual Practice questions per limb. Located at `references/asparsa_yoga_scrolls.md`.
- Conceptual archaeology synthesis — maps old concept document patterns to current architecture, includes preliminary limb-to-feature mapping across all three domains. Located at `references/conceptual_archaeology.md`.

### The philosophical lineage is mapped (NEW)
Reviewed 8 source documents spanning the full evolution of this project's thinking:

```
Ra/Thoth/Hermes (perennial philosophy research)
    → Seven Hermetic Principles (structural extraction)
    → Adaptive Coherence Model (system design through Hermetic lens)
    → Guiding Principles of Resonant Intelligence (AI behavioral spec)
    → Instructional Framework (meta-prompt encoding)
    → Asparśa Yoga (mature philosophical framework, Vedantic pivot)
```

The decisive shift: Hermetic framework emphasizes *mastery* (manipulating polarities). Yoga framework emphasizes *recognition* (perceiving without possessing). This is the difference between the magician model and the mirror model. The agenetic framework implements the mirror.

### Recurring structural patterns extracted (NEW)
Five patterns appear across ALL concept documents and map to current architecture:

1. **Three-flow pattern** → signal/semantic/meta domains
2. **Dual-layer architecture** (analog base + digital refinement + adaptive controller) → signal/semantic/meta
3. **Seed-branch-prune cycle** → genetic/sleep meta-domain lifecycle
4. **Alchemical stages** (Nigredo → Albedo → Citrinitas → Rubedo) → stimulus processing pipeline states
5. **Value cycle 0-to-1 resting at 0.5** → limb weight calibration model

The 0-to-1 range emerged independently in the signal domain implementation (normalized feature values) without explicit reference to the old specs. The structural insight was correct even when the surface implementation context was completely different.

## Sequencing Rationale

**Why signal domain first:** Cheapest to implement, validates the core architectural insight, and every other system depends on it. Conscious needs signal reports as input. Sleep needs signal patterns to consolidate. Can't build downstream without upstream.

**Why yoga implementation before conscious:** The conscious layer will be the first LLM-backed system. Its behavior should be shaped by the orientational field — but the field is currently just 18 labels with uniform weights. Implementing conscious against a placeholder field means we'd have to redo the integration once the field is real. Better to get the field right first.

**Why documentation/cleanup now:** Multiple sessions of planning work have produced reference material (yoga scrolls, conceptual archaeology synthesis, README, DEVLOG) that exists in chat but hasn't been fully synchronized to the repo. The CLI agent needs to see the current state of the project accurately before receiving build directives. Additionally, CLAUDE.md needs to reflect the actual project structure so future cold-start agents orient correctly.

## Open Questions

- **Is seven the right number of systems?** The hexagonal packing question from ARCHITECTURE.md. Not blocking anything but worth revisiting as implementation reveals whether any system is doing double duty or is structurally redundant.

- **What constitutes effective sleep consolidation?** The sleep system is the linchpin — it's the only system that writes to genetic expression and the orientational field. What should pruning, strengthening, and reference signal optimization actually look like in practice?

- **How minimal can the genetic seed be?** The compression ratio question. Current genetic layer is 18 limbs + principles. Is that the right level of specification, or should it be more/less?

- **Cache eviction strategy:** Signal pattern cache grows unboundedly. Apoptotic at 10k is a safety valve, not a solution. Sleep needs a real pruning strategy — which patterns to keep, which to merge, which to discard.

- **Immune vaccination:** Immune log starts empty. Should there be a set of baseline threat patterns seeded from the genetic layer? Biological immune systems have innate recognition of conserved pathogen features.

- **Limb-to-feature mapping verification (NEW):** The preliminary mapping in conceptual_archaeology.md assigns limbs to signal/semantic/meta domain features. Some assignments are confident (Prakāśa → signal characterization, Nivṛtti → output suppression), others tentative (Ārēka → hard boundaries, Fourfold State → mode tracking). These need to be tested experimentally — "the only way to know is to play around."

## Threads to Resume

1. **Limb-to-feature mapping** — encode yoga limbs as testable system behaviors. Source material now available. This is the next major design task after repo cleanup.
2. **Conscious layer** — first LLM-backed system. Blocked on yoga implementation (field should be real before conscious uses it).
3. **Motor layer** — reverse transduction. Could be implemented independently of conscious.
4. **Sleep layer** — transfer function optimization. Most architecturally critical remaining system. Blocked on understanding what the orientational field should look like post-optimization.
5. **Weight system redesign** — move from uniform 1.0 to 0.5 midpoint model. Blocked on sleep implementation (sleep is what modifies weights).
