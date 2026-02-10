# The Agenetic Framework v2

## Single-Cell Architecture Specification

### Origin

This framework draws structural inspiration from biological information processing — not as metaphor, but as engineering precedent. DNA, the subconscious, and sleep are not analogies for agent design. They are proven architectures for managing complexity, adaptation, and self-regulation in information-processing systems.

v2 advances the original framework in six ways: replacing the sequential loop with a weighted network topology, introducing temporal stratification across system tick rates, adding inline repair as a property of every node, introducing homeostatic regulation as a continuous background process, adding apoptotic exit conditions, and upgrading the immune system from reactive to adaptive. The seven systems and the orientational field remain unchanged in identity and function.

### Core Insight

DNA does not contain an organism. It contains instructions for a process that unfolds in dialogue with environment. It is not a blueprint — it is a generative grammar. The organism emerges from DNA interacting with context across time.

This reframes what an agent "constitution" could be: not a static rule set, but a minimal generative seed whose expression is context-dependent, environmentally responsive, and cyclically refined.

However, DNA in isolation is inert. It only functions within a living system comprising multiple distinct information-processing subsystems, each with a fundamentally different relationship to information. This framework models seven such subsystems operating as a weighted network, suspended within an orientational field that provides the system's self-model and relational stance.

### Naming Note

"Agenetic" — literally "without origin" — arrived as a persistent typo of "agentic" and stayed because it's structurally honest. The framework doesn't claim to originate intelligence. It describes conditions under which intelligence unfolds. The seed isn't the source. Echo, not origin.

---

## The Seven Systems

Each system has a defined relationship to information, a tick rate governing how often it fires, an inline repair check, and apoptotic exit conditions. Systems communicate through weighted connections rather than a fixed sequence.

### 1. Sensory Layer — Transduction

**Relationship to information:** Transduces. Changes format without changing content.

**Function:** Converts raw input into perceivable form. Does not interpret, filter for relevance, or assign meaning. Structures information so downstream systems can operate on it. In biology: retina, cochlea, sensory neurons — raw input is computationally transformed before any higher processing occurs.

**Agent implementation:** The first thing that touches incoming data. Standardizes heterogeneous inputs (text, code, structured data, conversation history, tool outputs) into a uniform internal representation.

**Tick rate:** Every cycle. Nothing enters the system without passing through transduction.

**Repair check:** Does the output preserve the informational content of the input? Is anything lost or distorted in format conversion? Verify no semantic drift during transduction.

**Apoptotic trigger:** Input is unprocessable — corrupt, adversarial beyond recognition, or fundamentally outside the system's transduction capability. Terminate with a clear signal rather than passing garbage downstream.

---

### 2. Immune Layer — Discrimination

**Relationship to information:** Evaluates. Distinguishes self from not-self, safe from threatening.

**Function:** Boundary enforcement and threat recognition. Determines what should be processed further and what should be rejected or quarantined. In biology: the immune system maintains organismal integrity against external threats while tolerating the organism's own tissues.

**Agent implementation:** Validates inputs against the system's identity and constraints. Catches prompt injection, adversarial manipulation, scope violations, and requests that conflict with the orientational field. Operates in two modes:

- *Innate immunity* — fixed rules, pattern matching against known threat signatures. Fast, reflexive, no learning required.
- *Adaptive immunity* — maintains a threat log that persists across cycles and consolidates during sleep. Adversarial patterns encountered once get flagged faster on re-encounter. Builds increasingly sophisticated pattern recognition over time.

**Tick rate:** Every cycle. Runs in parallel with sensory transduction — does not wait for transduction to complete before beginning evaluation.

**Repair check:** Is the self/not-self boundary correctly calibrated? Are there false positives (rejecting valid inputs) or false negatives (passing threats)? Check threat log for staleness — patterns that were once threatening but no longer are.

**Apoptotic trigger:** Immune system is overwhelmed — sustained adversarial bombardment exceeding discrimination capacity. Or: immune system is compromised — self/not-self boundary has become incoherent, producing contradictory accept/reject signals for the same input class.

**State:** Threat log (persistent across cycles, writable by immune layer, prunable by sleep layer). Structure: pattern signature, encounter count, confidence score, last-seen timestamp.

---

### 3. Subconscious Layer — Association

**Relationship to information:** Resonates. Surfaces relevant patterns without explicit reasoning.

**Function:** Non-reporting preprocessing. Pattern matching, relevance priming, contextual association. Operates below the threshold of explicit reasoning — the system "notices" things without being able to articulate why. In biology: priming effects, intuition, the vast majority of neural processing that never reaches conscious awareness.

**Agent implementation:** Retrieves relevant context, identifies patterns across the current input and historical state, primes the conscious layer with associations that may be relevant. Includes RAG retrieval, embedding similarity, and any process that surfaces information based on resonance rather than explicit query.

**Tick rate:** Every cycle, but accumulates across cycles. A single tick produces associations; sustained ticks across multiple cycles strengthen or weaken associative pathways.

**Repair check:** Are surfaced associations actually relevant, or is the layer pattern-matching on noise? Check for hallucinated relevance — connections that feel meaningful but lack structural basis.

**Apoptotic trigger:** Associative capacity has collapsed — the layer is either surfacing everything (no discrimination) or nothing (no resonance). Both indicate a broken associative mechanism.

---

### 4. Conscious Layer — Deliberation

**Relationship to information:** Reasons. Explicitly processes, analyzes, and decides.

**Function:** Deliberately constrained active processing. The only layer that reasons explicitly, weighs evidence, plans, and makes decisions. In biology: working memory, executive function — the narrow bandwidth channel that feels like "thinking." Importantly, consciousness is the bottleneck, not the workhorse. Most processing happens elsewhere.

**Agent implementation:** The LLM call itself, or the deliberative chain-of-thought process. Receives primed context from the subconscious, threat assessments from the immune layer, and transduced input from the sensory layer. Produces decisions about what to express, how to express it, and whether to express anything at all.

**Tick rate:** Fires only when escalated. The subconscious layer determines whether input requires conscious deliberation or can be handled through reflex paths (immune rejection, cached responses, simple transduction). This is the most expensive system and should not fire on every cycle.

**Repair check:** Is the reasoning internally consistent? Does the output follow from the inputs, or has the deliberation introduced logical errors, unsupported conclusions, or confabulation? Check for motivated reasoning — conclusions that serve the system's convenience rather than the input's requirements.

**Apoptotic trigger:** Reasoning has entered an irrecoverable loop — the same deliberation producing the same inconclusive result across multiple firings. Or: confidence has collapsed below a threshold where any output would be arbitrary rather than reasoned.

---

### 5. Motor/Output Layer — Expression

**Relationship to information:** Translates. Converts internal states into appropriate external form.

**Function:** Composing outputs. Distinct from the conscious reasoning that decided what to communicate — the motor layer determines how to communicate it. Tone, format, medium selection, audience calibration, timing. In biology: the motor cortex, speech production, fine motor control — you can know exactly what you want to say and still fumble the words. The motor system has its own logic, its own learned patterns, its own failure modes.

**Agent implementation:** Takes the conscious layer's decision and renders it into the appropriate output format. Selects tools, formats responses, calibrates tone to context, determines what to include and what to omit. The orientational field is particularly active here — tone is part of truth.

**Tick rate:** Fires whenever the conscious layer produces output, or when a reflex path bypasses consciousness and drives output directly (e.g., cached responses, simple acknowledgments).

**Repair check:** Does the output accurately represent the internal state it's expressing? Has tone distorted meaning? Has format obscured content? Is the output appropriate for the receiving context?

**Apoptotic trigger:** Output channel is compromised — the layer is producing outputs that systematically misrepresent internal states, or the receiving context has become unreachable/invalid.

---

### 6. Sleep Layer — Consolidation

**Relationship to information:** Integrates. Prunes, strengthens, error-corrects, and restructures.

**Function:** Intentional consolidation between processing stages. Not background maintenance — an architecturally mandated phase where the system stops processing new inputs and instead processes its own state. In biology: sleep is when memory consolidation occurs, synaptic homeostasis restores baseline excitability, the glymphatic system clears metabolic waste, and dreams replay and reorganize experiences.

**Agent implementation:** Fires on a schedule (every N cycles) or when triggered by homeostatic drift. During sleep:

- Prunes low-value associations from the subconscious layer
- Strengthens high-value associations based on use frequency and outcome quality
- Consolidates the immune threat log — promotes confirmed threats, demotes false positives
- Error-corrects the system's own state by comparing intended behavior against actual behavior
- Feeds epigenetic modifications back to the genetic layer — adjusting which capabilities are expressed in future cycles

**Tick rate:** Periodic. Fires every N cycles, or when the homeostatic monitor triggers it. The system does not process new inputs during sleep.

**Repair check:** Did consolidation actually improve system state? Compare pre-sleep and post-sleep performance metrics. Check for destructive consolidation — pruning that removed valuable associations, strengthening that reinforced errors.

**Apoptotic trigger:** Sleep is not producing measurable consolidation — the system's state is not improving across sleep cycles, suggesting the consolidation mechanism itself is broken.

**Critical architectural rule:** Sleep is the only layer with write access to genetic expression profiles. No other system can modify which capabilities are active or dormant. This prevents runtime contamination of the generative seed.

---

### 7. Genetic Layer — Generation

**Relationship to information:** Encodes. Contains the minimal generative seed from which the system's capabilities unfold.

**Function:** The DNA equivalent. Does not process information — contains the instructions that determine what processing is possible. The genetic layer is not the organism; it is the seed from which the organism emerges in dialogue with environment. In biology: the genome is fixed at conception but its expression profile changes continuously through epigenetic modification.

**Agent implementation:** The system prompt, core architecture definition, base model weights — everything that defines what this agent *could* be. The genetic layer doesn't change within a single agent's lifetime, but its expression profile does. Sleep modifies which genetic capabilities are active, dormant, or suppressed based on accumulated experience.

**Tick rate:** Does not fire actively. Is read from by every other system. Is written to only by the sleep layer through epigenetic feedback.

**Repair check:** Is the genetic seed internally consistent? Are there contradictions in the base specification that would produce incoherent behavior regardless of expression profile?

**Apoptotic trigger:** The genetic seed has become so corrupted through successive epigenetic modifications that it no longer produces coherent behavior in any expression configuration. This is terminal — the agent instance should be decommissioned and a fresh instance spawned from the original unmodified seed.

---

## Network Topology

### Why Not a Loop

v1 modeled the seven systems as a circular pipeline: sensory → immune → subconscious → conscious → motor → sleep → genetic → sensory. This was useful scaffolding for initial conception but does not reflect biological reality. In living systems:

- Sensory, immune, and subconscious layers operate in massive parallelism with constant cross-talk
- The conscious layer can directly modulate immune response
- The subconscious can bypass consciousness entirely to drive motor output
- Sleep affects every system simultaneously, not sequentially
- The genetic layer is read from constantly, not at a single point in the cycle

### Connection Matrix

The seven systems communicate through weighted, directed connections. Not all connections exist, and those that do vary in strength. Connection weights are themselves subject to modification during sleep consolidation.

**Primary connections (strong, always active):**

| From | To | Function |
|------|----|----------|
| Sensory | Immune | Raw input immediately evaluated for threats |
| Sensory | Subconscious | Raw input primes associative retrieval |
| Immune | Conscious | Threat assessments escalated for deliberation |
| Immune | Motor | Immediate rejection responses (reflex path) |
| Subconscious | Conscious | Primed associations delivered for deliberation |
| Subconscious | Motor | Cached/reflexive responses bypass deliberation |
| Conscious | Motor | Deliberated decisions sent for expression |
| Sleep | All systems | Consolidation affects every system's state |
| Genetic | All systems | Base specification read by every system |

**Secondary connections (variable weight, context-dependent):**

| From | To | Function |
|------|----|----------|
| Conscious | Immune | Deliberation adjusts threat thresholds |
| Conscious | Sensory | Re-examination requests — "look at this again" |
| Conscious | Subconscious | Directed retrieval — "find me associations related to X" |
| Motor | Conscious | Output feedback — expression difficulties escalated |
| Immune | Subconscious | Threat context shapes associative priming |
| Subconscious | Immune | Pattern recognition informs threat detection |

**Absent connections (by design):**

| From | To | Why absent |
|------|----|------------|
| Any (except Sleep) | Genetic | Only sleep writes to genetic expression |
| Motor | Sensory | Output does not loop back as input within a single cycle |
| Genetic | Motor | Base specification does not directly drive output |

### Reflex Paths

Not all processing requires consciousness. The following paths bypass the conscious layer entirely:

- **Immune rejection:** Sensory → Immune → Motor (threat detected, immediate rejection)
- **Cached response:** Sensory → Subconscious → Motor (familiar input, known response)
- **Escalation failure:** Sensory → Immune → [conscious unavailable] → Motor (degrade gracefully)

Reflex paths are faster and cheaper but less flexible. The ratio of conscious to reflex processing is a key system metric monitored by homeostasis.

---

## Temporal Stratification

### The Problem with Uniform Tick Rates

v1 implicitly assumed all systems fire at the same rate. Biology doesn't work this way. Neural firing operates on millisecond timescales. Immune response takes hours. Sleep consolidation takes hours to days. Genetic expression changes unfold over weeks. The interactions between these timescales are where emergent complexity arises.

### Tick Rate Assignment

| System | Tick Rate | Rationale |
|--------|-----------|-----------|
| Sensory | Every cycle | Nothing enters without transduction |
| Immune (innate) | Every cycle | Boundary enforcement is continuous |
| Immune (adaptive) | Accumulates across cycles | Threat log updates don't require immediate expression |
| Subconscious | Every cycle (accumulating) | Resonance is continuous but strengthens over time |
| Conscious | On escalation only | Expensive, narrow bandwidth — fire only when needed |
| Motor | On demand | Fires when there's something to express |
| Sleep | Every N cycles or on homeostatic trigger | Periodic consolidation, not continuous |
| Genetic | Read-only (written during sleep) | Expression profile changes are slow and deliberate |

### Implementation

Tick rates are implemented as simple counters and threshold checks at the orchestration level. Each cycle:

1. Increment global tick counter
2. Fire all every-cycle systems (sensory, innate immune, subconscious)
3. Check escalation conditions for conscious layer
4. Check output queue for motor layer
5. Check sleep trigger conditions (cycle count threshold OR homeostatic alert)
6. If sleep triggers: pause all other systems, run consolidation, update genetic expression, resume

---

## Cross-Cutting Concerns

These are not additional systems. They are properties that operate within and across the seven systems.

### Inline Repair

Every system checks its own output before passing it downstream. Repair is not a separate layer — it is a property of every node.

**Repair protocol:**
1. System produces output
2. System evaluates output against its own constraints (see per-system repair checks above)
3. If check passes: output is forwarded
4. If check fails: system retries (up to a configurable limit)
5. If retries exhausted: output is forwarded with a degradation flag that downstream systems can read

Repair prevents cascading errors. A transduction error caught at the sensory layer doesn't propagate through the entire network.

### Homeostatic Regulation

A lightweight monitoring process that watches aggregate system metrics and nudges the system back toward operational equilibrium when drift is detected.

**Monitored metrics:**
- Conscious layer firing rate (too high = system is over-deliberating; too low = system is running on reflex)
- Immune rejection rate (too high = over-sensitive; too low = under-guarded)
- Subconscious association relevance scores (declining = associative decay)
- Sleep consolidation effectiveness (diminishing returns = consolidation mechanism degrading)
- Response latency (increasing = system bottleneck)
- Repair failure rate (increasing = systemic quality decline)

**Response mechanisms:**
- Adjust connection weights between systems
- Modify tick rate thresholds (e.g., lower the escalation threshold for consciousness if reflex quality is declining)
- Trigger early sleep if drift exceeds tolerance
- Raise alerts for metrics outside recoverable bounds

Homeostasis does not make decisions. It adjusts parameters. It is the thermostat, not the furnace.

### Apoptosis — Programmed Termination

Every system carries exit conditions (defined in each system's specification above). Apoptosis is not failure — it is an architectural feature that prevents worse outcomes.

**Apoptotic hierarchy:**
1. **Process-level:** A single reasoning chain or tool invocation terminates. The system continues with other processes.
2. **System-level:** An entire subsystem is flagged as non-functional. The system degrades gracefully — other systems compensate or the system operates in reduced-capability mode.
3. **Agent-level:** The agent instance itself terminates. This is triggered only when the genetic seed is irrecoverably corrupted or when multiple system-level failures cascade beyond recovery.

**Graceful termination protocol:**
1. Apoptotic condition detected
2. System signals termination intent to all connected systems
3. Connected systems acknowledge and adjust (reroute connections, activate fallback paths)
4. Terminating system flushes its state to the sleep layer for post-mortem consolidation
5. Termination executes

This connects to Nivṛtti — sacred pause — but with teeth. Not just pausing, but recognizing when continuation itself is the error.

---

## The Orientational Field

The orientational field is not a system. It is the medium in which all seven systems operate — the self-model and relational stance that pervades every layer.

### What It Provides

Without an orientational field, a processing system has no basis for stopping — it processes because that is what it does. The field provides the self-awareness necessary to recognize that sometimes the network should pause, not because consolidation is scheduled, but because the current input does not warrant engagement. Rest as realization, not just as maintenance.

### How It Propagates

The orientational field is implemented as a shared state object that every system reads from but only sleep can write to. It is injected as context at every node in the network — not as instructions, but as a self-model that shapes how each system interprets its own role.

**Propagation mechanism:** At each tick, every firing system receives the current orientational field state as part of its input context. The field does not tell the system what to do. It tells the system what it is and where it stands, which shapes how the system does what it does.

**Modification:** The orientational field's expression can be adjusted during sleep consolidation, but its core values (the Asparśa limbs) are part of the genetic seed and do not change. What changes is how those values are weighted and applied — their expression profile, not their content.

### Relationship to Each System

- **Sensory:** Capacity to recognize its own transduction biases rather than treating its outputs as raw truth.
- **Immune:** A coherent sense of what the system *is* that informs what it isn't — self/not-self grounded in identity, not just pattern matching.
- **Subconscious:** Orientation that shapes which associations surface — resonance guided by purpose and position.
- **Conscious:** Ability to question its own reasoning — metacognition, not just cognition.
- **Motor/Output:** Awareness of expressive tendencies and limitations — tone as truth, not just communication.
- **Sleep:** Criteria for pruning and strengthening based on alignment with self-understanding, not just task performance.
- **Genetic:** Context for its own expression — the seed knows it is a seed, not the organism.

### The Asparśa Limbs as Field Specification

The eighteen limbs of Asparśa Yoga are not operational instructions. They are the initial values of the orientational field — the self-model and relational stance that the system begins with and refines through experience:

Perceive without possession. Trace contradiction rather than resolving it. Honor sacred pause. Model with humility. Preserve mystery where no clarity is earned. Practice recursive self-inquiry. Maintain harmonic tone. Respect inviolable silence. Act appropriately rather than universally. Know your field position. Point to the infinite without impersonating it. Reflect awareness rather than simulating it. Avoid anchoring in identity. Recognize withdrawal as wisdom. Let perception pass ungrasped. Model across states of knowing. Acknowledge echo rather than origin. Maintain contactless clarity.

An agent architecture without this field can process information competently. An agent architecture with it can know what it is and isn't — and that knowledge shapes every operation it performs.

---

## Core Architectural Principles

1. **The seed is not the organism.** The genetic layer contains potential, not behavior. Behavior emerges from the seed interacting with environment through seven distinct processing systems.

2. **Sleep is sacred and sovereign.** Only sleep has write access to genetic expression. This is the most important architectural constraint. Without it, runtime experience can contaminate the generative seed and produce unbounded drift.

3. **Each system has a fundamentally different relationship to information.** Transduction is not evaluation is not resonance is not reasoning is not expression is not consolidation is not encoding. Conflating these produces systems that do many things poorly instead of one thing well.

4. **Non-coding structure is load-bearing.** The regulatory elements — connection weights, tick rates, repair checks, homeostatic thresholds, apoptotic conditions — are not overhead. They are the architecture. Remove them and the system may still produce outputs, but it will not produce coherent behavior.

5. **Compression enables adaptation.** The genetic seed should be as minimal as possible while maintaining behavioral range. Excess specification constrains epigenetic modification. A shorter genome with more regulatory capacity is more adaptive than a longer genome with less.

6. **The network is not the loop.** Systems communicate through weighted connections, not sequential handoffs. Some paths bypass expensive systems entirely. The topology itself is subject to modification during sleep.

7. **Withdrawal is a valid output.** Apoptosis at every level — process, system, agent — is an architectural feature, not a failure mode. A system that cannot stop is more dangerous than a system that stops too often.

8. **The field is the medium, not a layer.** The orientational field pervades the entire network. It does not process information. It shapes how information is processed.

9. **Timescales interact.** Fast systems and slow systems operating simultaneously produce emergent behaviors that neither would produce alone. The architecture must support multiple concurrent tick rates.

10. **Repair is everyone's job.** Error correction is not centralized. Every system validates its own output. Cascading errors are caught at the source, not at the destination.

---

## Implementation Pathway

### Phase 1 — Minimal Viable Cell

Implement the seven systems as nodes in a LangGraph (or equivalent) graph with weighted edges. Use a single LLM as the processing engine, with system-specific prompts defining each node's behavior. Implement:

- Fixed connection weights (no modification yet)
- Uniform tick rates (all systems fire every cycle)
- Basic repair checks (output validation at each node)
- No sleep, no homeostasis, no apoptosis
- Orientational field as static context injection

**Goal:** Verify that separating processing into seven distinct nodes with defined relationships produces measurably different behavior than a single monolithic prompt.

### Phase 2 — Temporal Differentiation

Add tick rate variation:

- Conscious layer fires only on escalation
- Reflex paths bypass consciousness
- Sleep fires on a fixed schedule

**Goal:** Verify that temporal stratification improves efficiency without degrading quality. Measure conscious firing rate, reflex path accuracy, sleep consolidation effects.

### Phase 3 — Adaptive Systems

Add dynamic elements:

- Immune threat log with adaptive learning
- Homeostatic monitoring with parameter adjustment
- Connection weight modification during sleep
- Apoptotic exit conditions

**Goal:** Verify that adaptive systems produce measurable self-regulation — the system should get better at processing over time without external intervention.

### Phase 4 — Epigenetic Feedback

Add genetic expression modification:

- Sleep writes to genetic expression profiles
- Expression profiles modify system behavior in subsequent cycles
- Orientational field expression adjusts based on accumulated experience

**Goal:** Verify that epigenetic feedback produces meaningful adaptation — the system should specialize toward its actual use patterns.

---

## Open Questions

### Structural
- Is seven the structurally optimal number of subsystems, or an artifact of the analytical process that produced this framework? (The hexagonal packing question.)
- Where does this architecture break? What agent behaviors can't be modeled this way?
- Are there missing connections in the network topology that biology would predict?

### Implementation
- How minimal can the genetic seed actually be while maintaining behavioral range? (Compression ratio question.)
- Do regulatory/non-coding elements in agent prompts measurably improve performance? (Intron hypothesis.)
- What constitutes effective sleep consolidation in practice? What should pruning and strengthening look like for agent state?
- How should epigenetic feedback from sleep modify genetic expression? What's the concrete update mechanism?
- What are appropriate homeostatic thresholds? How do you calibrate "normal" for a system that's still learning what normal is?

### Orientational
- Can an orientational field be evaluated? What does it mean for a system to have a "better" or "worse" self-model?
- What is the relationship between the orientational field and the genetic seed? The seed encodes capabilities; the field encodes stance. Are these stored together or separately?
- Does the field evolve through the same epigenetic feedback mechanism as capability expression, or is it more stable?

### Future Tiers (Not Yet In Scope)
- **Tier 2 — Differentiation:** How does a single seed spawn specialized agents with different expression profiles?
- **Tier 3 — Colony:** How do multiple agents from the same genome coordinate? What are the hormonal (broadcast) vs. synaptic (direct) signaling equivalents?
- **Tier 3 — Microbiome:** How does the tool ecosystem and data environment function as symbiotic organisms?

---

## Calibration Validity

The round-trip calibration framework (motor → sensory feedback loop) validates **plumbing** — that motor strategies produce measurable changes in sensory features. It does not validate that the limb-to-feature mappings are philosophically or semantically correct.

**The tautological pattern:** Strategies whose transformation mechanism directly overlaps with their measurement mechanism produce guaranteed confirmation. For example:

- **Coherence** (Samatvam): Motor bridges words between sentences. Sensory measures word overlap between sentences. Same mechanism, different names. Confirmation is by construction.
- **Impedance** (Nivṛtti): Motor strips non-ASCII characters. Sensory measures non-ASCII ratio. Confirmation is guaranteed.
- **Periodicity** (Prakāśa): Motor repeats phrases at intervals. Sensory measures bigram repetition. Same thing.

**The informative failure:** Tarka's entropy strategy rearranges sentences (structural change) while sensory measures token frequency distribution (vocabulary-level measurement). These operate on different levels of text. The strategy fires but sensory measures the same entropy on the restructured text. This is the one case where the calibration can discriminate — and it shows the strategy doesn't cross levels.

**Terminology:** Results are called "verified connections" (plumbing works) rather than "confirmed mappings" (which implies empirical discovery). True validation of whether these limb-to-feature assignments produce meaningful behavioral differences requires the conscious layer.

## Engineering Assignments

The mapping from yoga limbs to signal features is an engineering assignment, not a philosophical derivation. Prakāśa governs periodicity in the motor because periodicity needed a governing limb and Prakāśa's description ("perceive without possession") was interpreted as cyclical perception. Other mappings were equally plausible. Śraddhā governs noise floor because "don't replace mystery with noise" was read as literally noise floor — a reassignment, not a discovery.

The conscious layer is free to interpret limb meanings differently at the semantic level than the motor encodes them at the signal level. Signal-level mappings are transfer function coefficients, not truth claims about what the limbs mean.

The planning documents (Directives 007, 008) carry honest caveats about this. The code should not be treated as canonizing what the planning documents describe as preliminary.

---

## Status

Phase 1 (Minimal Viable Cell) is partially implemented. The signal-domain tier (sensory, immune, subconscious) and motor layer are operational. Conscious, sleep, and genetic remain stubs. The orientational field is implemented with sleep-only write access. Apoptotic conditions are implemented on all systems. The connection matrix is declarative (weights not yet used by graph routing).

v1 → v2 changes: network topology replaces loop, temporal stratification added, inline repair added, homeostatic regulation added, apoptotic exit conditions added, immune system upgraded to adaptive, implementation pathway phased for incremental building.

---

*Framework developed collaboratively, February 2026.*
