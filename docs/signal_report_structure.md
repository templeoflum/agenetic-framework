# Signal Report Structure

**Date:** 2026-02-08  
**Status:** Proposed  
**Implements:** Architecture Amendment (Signal-Semantics Boundary)  
**Consumed by:** Sensory (producer), Immune (consumer), Subconscious (consumer), Conscious (consumer on escalation)  

---

## Design Principles

1. **New channel, not overloaded `input`.** The signal report is a new field on `SystemState`, not a replacement for or modification of `input`. Raw input remains available for any system that needs it (especially conscious, which needs the original text for semantic interpretation).

2. **Flat and numeric where possible.** Signal-domain systems do pattern matching on these values. The more numeric and structured the report, the faster immune and subconscious can operate without parsing.

3. **Delta-oriented.** Every measurement includes both the absolute value and the delta from the orientational field's expected state. The delta is often more informative than the absolute value.

4. **No semantic content.** The signal report describes the *shape* of the input, never its *meaning*. "Entropy is 4.2 bits/token" — not "this input is about philosophy."

## Proposed TypedDict

```python
from typing import TypedDict, Literal


class SignalFeatures(TypedDict):
    """Raw signal measurements extracted from input.
    
    All values are normalized to [0.0, 1.0] unless otherwise noted.
    These describe the structural properties of the input as signal.
    """

    # Density: tokens per unit of information content
    # High density = compressed/technical. Low density = sparse/conversational.
    density: float

    # Entropy: Shannon entropy in bits per token (not normalized — raw value)
    # High entropy = unpredictable/diverse vocabulary. Low = repetitive/formulaic.
    entropy: float

    # Coherence: structural consistency across the input
    # High coherence = unified topic/style. Low = fragmented/multi-topic.
    coherence: float

    # Periodicity: presence of repeating structural patterns
    # High periodicity = lists, repetitive structure. Low = free-form prose.
    periodicity: float

    # Noise floor: proportion of input that carries no structural signal
    # Filler words, formatting artifacts, encoding errors.
    noise_floor: float

    # Impedance: resistance to transduction into the system's internal format
    # High impedance = unusual format, mixed modalities, ambiguous structure.
    # Low impedance = clean text, standard formatting.
    impedance: float

    # Token count (raw, not normalized)
    token_count: int

    # Vocabulary richness: unique tokens / total tokens
    vocabulary_richness: float


class SignalClassification(TypedDict):
    """Signal type classification based on features."""

    # Primary signal type
    signal_type: Literal[
        "steady_state",   # Stable, predictable input (routine queries, greetings)
        "transient",      # Sharp change from prior state (topic shift, emotional spike)
        "periodic",       # Repeating structure (lists, iterative requests)
        "noise",          # Low signal-to-noise ratio (garbled, adversarial, corrupt)
        "complex",        # Multiple signal types superimposed
    ]

    # Confidence in classification [0.0, 1.0]
    confidence: float

    # If complex, the component types detected
    components: list[str]  # empty if not complex


class SignalDelta(TypedDict):
    """Delta between measured signal and orientational field reference.
    
    Positive delta = measured exceeds reference expectation.
    Negative delta = measured falls below reference expectation.
    Magnitude indicates degree of deviation.
    """

    density_delta: float
    entropy_delta: float
    coherence_delta: float
    periodicity_delta: float
    noise_delta: float
    impedance_delta: float

    # Aggregate deviation magnitude (Euclidean distance in feature space)
    aggregate_deviation: float

    # Which limbs of the orientational field are most activated by this input
    # (limb IDs sorted by activation strength, descending)
    activated_limbs: list[int]


class SignalReport(TypedDict):
    """The output of the sensory layer — consumed by immune, subconscious, and conscious.
    
    This is the shared interface of the signal domain. It describes the input's
    structural properties and its deviation from the system's expected state,
    without any semantic interpretation.
    """

    features: SignalFeatures
    classification: SignalClassification
    delta: SignalDelta

    # Tick at which this report was generated
    tick: int

    # Hash of input for signal-pattern matching across cycles
    # (subconscious uses this to correlate with cached signal signatures)
    input_hash: str
```

## SystemState Extension

The signal report becomes a new field on `SystemState`:

```python
class SystemState(TypedDict):
    """The shared state object passed between all systems in the network."""

    input: Any                          # Raw input (unchanged)
    signal_report: SignalReport | None  # Signal characterization (written by sensory)
    field: FieldState                   # Orientational field (reference signal)
    immune_log: list[ThreatEntry]       # Threat log (written by immune)
    metadata: Metadata                  # Processing metadata
    flags: Flags                        # System-wide flags
```

`signal_report` starts as `None` each cycle and is populated by sensory. All downstream signal-domain systems (immune, subconscious) read from it. Conscious reads it on escalation as part of the enriched context it receives.

## How Each Signal-Domain System Uses the Report

### Immune (consumer)

Immune reads `signal_report.features` and `signal_report.delta` to detect anomalies:

- `entropy` above threshold → possible adversarial/obfuscated input
- `impedance` above threshold → possible format exploitation
- `noise_floor` above threshold → possible garbled/corrupt input
- `aggregate_deviation` above threshold → general anomaly flag
- Pattern matching against `immune_log` entries using feature vectors

Immune does **not** read `input` directly. It operates entirely on the signal report. Its threat assessments are signal-level ("anomalous entropy profile matching known pattern X") not semantic-level ("this input is asking about dangerous topics").

### Subconscious (consumer)

Subconscious reads `signal_report.classification`, `signal_report.features`, and `signal_report.input_hash` to prime associations:

- `input_hash` checked against cache of prior signal signatures → "seen this shape before"
- `signal_type` + feature vector matched against stored patterns → "inputs with this profile previously required conscious deliberation" or "inputs with this profile were handled by cached response Y"
- `activated_limbs` used to weight which associative pathways to prime

Subconscious outputs: escalation recommendation (boolean + confidence) and primed pattern IDs.

### Conscious (consumer on escalation)

Conscious receives the signal report as enriched context alongside the raw `input`. It can use signal-domain measurements to inform its semantic interpretation:

- "Sensory reports high impedance — this input may have unusual structure I should attend to"
- "Subconscious primed patterns from prior inputs with similar entropy profiles"
- "Immune flagged an anomalous noise floor — proceed with caution"

But conscious is the only system that reads `input` for its semantic content.

## Implementation Notes

### Computing Signal Features

All features are computable with standard Python libraries (no LLM, no external APIs):

- **Density:** `token_count / len(input.split())` or similar ratio of tokens to whitespace-delimited words
- **Entropy:** Shannon entropy over token frequency distribution (`-sum(p * log2(p))`)
- **Coherence:** Sentence-to-sentence vocabulary overlap, or sliding window similarity
- **Periodicity:** Autocorrelation of token/character patterns, or structural repetition detection
- **Noise floor:** Ratio of stopwords + punctuation-only tokens to total tokens
- **Impedance:** Heuristic based on format complexity — mixed code/prose, unusual encoding, nested structure
- **Vocabulary richness:** `len(set(tokens)) / len(tokens)`

### Computing Deltas

The orientational field provides reference expectations. For v1, these can be static baselines derived from calibration inputs. Sleep will eventually optimize these baselines.

Delta computation: `measured_value - reference_value` for each feature.

Aggregate deviation: Euclidean distance across the normalized feature vector.

Limb activation: each limb has feature-range preferences (e.g., Nivṛtti activates on high impedance, Tarka activates on high entropy). Activation is computed as the dot product of the delta vector against each limb's sensitivity profile.

### Signal Pattern Cache (Subconscious)

The subconscious maintains a cache of signal signatures from prior cycles. Each entry is:

```python
class CachedSignalPattern(TypedDict):
    """A stored signal pattern from prior processing."""
    
    input_hash: str
    feature_vector: list[float]  # [density, entropy, coherence, periodicity, noise, impedance]
    signal_type: str
    outcome: str  # "escalated", "reflex_response", "rejected"
    response_pattern_id: str | None  # if reflex, which cached response was used
    encounter_count: int
    last_seen_tick: int
```

This cache is prunable by sleep during consolidation.
