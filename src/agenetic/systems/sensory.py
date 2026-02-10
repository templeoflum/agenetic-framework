"""Sensory system — Signal Characterization.

Relationship to information: Transduces. Changes format without changing content.

Operates in the signal domain: extracts structural features from input without
interpreting semantic content. Measures density, entropy, coherence, periodicity,
noise floor, and impedance. Classifies by signal type. Computes delta from the
orientational field as reference signal.

Tick rate: Every cycle. Nothing enters the system without signal characterization.

Uses only Python stdlib — no LLM calls, no external dependencies.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from agenetic.systems.base import (
    BaseSystem,
    SignalClassification,
    SignalDelta,
    SignalFeatures,
    SignalReport,
    SystemState,
    compute_target_profile,
)


def _to_str(input_data) -> str:
    """Convert any input to its string representation."""
    if input_data is None:
        return ""
    if isinstance(input_data, str):
        return input_data
    return str(input_data)


def _compute_density(text: str) -> float:
    """Ratio of non-whitespace characters to total characters."""
    if not text:
        return 0.0
    non_ws = sum(1 for c in text if not c.isspace())
    return non_ws / len(text)


def _compute_entropy(tokens: list[str]) -> float:
    """Shannon entropy over token frequency distribution (bits per token)."""
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = len(tokens)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def _compute_coherence(text: str) -> float:
    """Average pairwise Jaccard similarity between adjacent sentences."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 2:
        return 1.0  # single sentence is maximally coherent with itself
    similarities = []
    for i in range(len(sentences) - 1):
        words_a = set(sentences[i].lower().split())
        words_b = set(sentences[i + 1].lower().split())
        if not words_a and not words_b:
            similarities.append(1.0)
            continue
        union = words_a | words_b
        if not union:
            similarities.append(1.0)
            continue
        intersection = words_a & words_b
        similarities.append(len(intersection) / len(union))
    return sum(similarities) / len(similarities) if similarities else 1.0


def _compute_periodicity(tokens: list[str]) -> float:
    """Ratio of repeated bigrams to total bigrams."""
    if len(tokens) < 2:
        return 0.0
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    counts = Counter(bigrams)
    repeated = sum(1 for bg in bigrams if counts[bg] > 1)
    return repeated / len(bigrams)


def _compute_noise_floor(tokens: list[str]) -> float:
    """Ratio of single-character tokens + pure-punctuation tokens to total."""
    if not tokens:
        return 0.0
    noise_count = 0
    for t in tokens:
        if len(t) == 1:
            noise_count += 1
        elif all(not c.isalnum() for c in t):
            noise_count += 1
    return noise_count / len(tokens)


def _compute_bigram_entropy(text: str) -> float:
    """Shannon entropy over character bigram frequency distribution.

    Responds to structural rearrangement (sentence splitting changes
    punctuation, capitalization, and whitespace patterns, which changes
    character bigram frequencies). This is distinct from token-frequency
    entropy which is preserved by sentence-level restructuring.
    """
    if len(text) < 2:
        return 0.0
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)]
    counts = Counter(bigrams)
    total = len(bigrams)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def _compute_impedance(text: str) -> float:
    """Heuristic composite impedance measure.

    Average of:
    (a) ratio of non-ASCII characters
    (b) ratio of lines containing mixed prose+code patterns
    (c) nesting depth indicator (max bracket/paren depth / 10, capped at 1.0)
    """
    if not text:
        return 0.0

    # (a) Non-ASCII ratio
    non_ascii = sum(1 for c in text if ord(c) > 127)
    non_ascii_ratio = non_ascii / len(text) if text else 0.0

    # (b) Mixed prose+code lines
    lines = text.split('\n')
    mixed_count = 0
    code_chars_pattern = re.compile(r'[{}()\[\];]')
    alpha_word_pattern = re.compile(r'[a-zA-Z]{2,}')
    for line in lines:
        if line.strip() and code_chars_pattern.search(line) and alpha_word_pattern.search(line):
            mixed_count += 1
    mixed_ratio = mixed_count / len(lines) if lines else 0.0

    # (c) Nesting depth
    max_depth = 0
    depth = 0
    for c in text:
        if c in '({[':
            depth += 1
            max_depth = max(max_depth, depth)
        elif c in ')}]':
            depth = max(0, depth - 1)
    depth_indicator = min(max_depth / 10.0, 1.0)

    return (non_ascii_ratio + mixed_ratio + depth_indicator) / 3.0


def _compute_input_hash(input_data) -> str:
    """SHA-256 hex digest of string representation, truncated to 16 chars."""
    text = _to_str(input_data)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


class SensorySystem(BaseSystem):
    """Signal characterization layer — extracts structural features from input.

    Operates entirely in the signal domain: no semantic interpretation,
    no LLM calls. Produces a SignalReport consumed by immune, subconscious,
    and (on escalation) conscious.
    """

    def __init__(self) -> None:
        super().__init__(
            name="sensory",
            description="Characterizes input as signal — density, entropy, coherence, periodicity, impedance",
        )
        self._consecutive_none_count = 0

    @property
    def tick_rate(self) -> str:
        return "every_cycle"

    def process(self, state: SystemState) -> SystemState:
        raw_input = state["input"]
        field_state = state["field"]
        tick = state["metadata"]["tick"]

        # Track consecutive None inputs for apoptotic condition.
        if raw_input is None:
            self._consecutive_none_count += 1
        else:
            self._consecutive_none_count = 0

        text = _to_str(raw_input)
        tokens = text.split() if text else []

        # Handle empty/None input: zeroed features, "noise" classification.
        if not text:
            features: SignalFeatures = {
                "density": 0.0,
                "entropy": 0.0,
                "coherence": 0.0,
                "periodicity": 0.0,
                "noise_floor": 0.0,
                "impedance": 0.0,
                "bigram_entropy": 0.0,
                "token_count": 0,
                "vocabulary_richness": 0.0,
            }
            classification: SignalClassification = {
                "signal_type": "noise",
                "confidence": 1.0,
                "components": [],
            }
            delta = self._compute_delta(features, field_state)
            report: SignalReport = {
                "features": features,
                "classification": classification,
                "delta": delta,
                "tick": tick,
                "input_hash": _compute_input_hash(raw_input),
            }
            return {**state, "signal_report": report}

        # Compute features.
        features = {
            "density": _compute_density(text),
            "entropy": _compute_entropy(tokens),
            "coherence": _compute_coherence(text),
            "periodicity": _compute_periodicity(tokens),
            "noise_floor": _compute_noise_floor(tokens),
            "impedance": _compute_impedance(text),
            "bigram_entropy": _compute_bigram_entropy(text),
            "token_count": len(tokens),
            "vocabulary_richness": len(set(tokens)) / len(tokens) if tokens else 0.0,
        }

        # Compute delta from orientational field reference.
        delta = self._compute_delta(features, field_state)

        # Classify signal.
        classification = self._classify(features, delta)

        report = {
            "features": features,
            "classification": classification,
            "delta": delta,
            "tick": tick,
            "input_hash": _compute_input_hash(raw_input),
        }
        return {**state, "signal_report": report}

    def _compute_delta(self, features: SignalFeatures, field_state) -> SignalDelta:
        """Compute delta between measured features and per-feature references.

        References are derived from the same target profile formulas the motor
        uses. This means sensory and motor share the same understanding of
        "expected" for a given field state. The delta is: how far is this
        feature from what the field expects.
        """
        # Per-feature references from shared target profile computation.
        ref = compute_target_profile(field_state)

        density_delta = features["density"] - ref["density"]
        entropy_delta = features["entropy"] - ref["entropy"]
        coherence_delta = features["coherence"] - ref["coherence"]
        periodicity_delta = features["periodicity"] - ref["periodicity"]
        noise_delta = features["noise_floor"] - ref["noise_floor"]
        impedance_delta = features["impedance"] - ref["impedance"]

        deltas = [density_delta, entropy_delta, coherence_delta,
                  periodicity_delta, noise_delta, impedance_delta]
        aggregate = math.sqrt(sum(d * d for d in deltas))

        # Activated limbs: sorted by abs(delta_feature) * limb_weight, descending.
        # Use the max absolute delta across features as the activation signal per limb.
        limbs = field_state.get("limbs", [])
        max_abs_delta = max(abs(d) for d in deltas) if deltas else 0.0
        activated = []
        for limb in limbs:
            product = max_abs_delta * limb["weight"]
            if product > 0.1:
                activated.append((limb["id"], product))
        activated.sort(key=lambda x: x[1], reverse=True)

        return {
            "density_delta": density_delta,
            "entropy_delta": entropy_delta,
            "coherence_delta": coherence_delta,
            "periodicity_delta": periodicity_delta,
            "noise_delta": noise_delta,
            "impedance_delta": impedance_delta,
            "aggregate_deviation": aggregate,
            "activated_limbs": [lid for lid, _ in activated],
        }

    def _classify(self, features: SignalFeatures, delta: SignalDelta) -> SignalClassification:
        """Classify the signal based on features and delta."""
        noise_floor = features["noise_floor"]
        periodicity = features["periodicity"]
        entropy_delta_abs = abs(delta["entropy_delta"])

        # Track which thresholds are triggered or close.
        triggered = []
        close = []  # within 80% of threshold

        # Noise check.
        if noise_floor > 0.4:
            triggered.append("noise")
        elif noise_floor > 0.32:  # 80% of 0.4
            close.append("noise")

        # Periodicity check.
        if periodicity > 0.3:
            triggered.append("periodic")
        elif periodicity > 0.24:  # 80% of 0.3
            close.append("periodic")

        # Transient check (entropy delta > 2.0).
        if entropy_delta_abs > 2.0:
            triggered.append("transient")
        elif entropy_delta_abs > 1.6:  # 80% of 2.0
            close.append("transient")

        # Classification logic.
        if not triggered:
            # Check if complex (multiple thresholds close).
            if len(close) > 1:
                signal_type = "complex"
                components = close
                confidence = 0.5  # uncertain
            else:
                signal_type = "steady_state"
                # Confidence: how far from any threshold.
                min_margin = 1.0
                if noise_floor > 0:
                    min_margin = min(min_margin, (0.4 - noise_floor) / 0.4)
                if periodicity > 0:
                    min_margin = min(min_margin, (0.3 - periodicity) / 0.3)
                confidence = max(min_margin, 0.3)
                components = []
        elif len(triggered) == 1:
            signal_type = triggered[0]
            # Confidence based on how far past threshold.
            if signal_type == "noise":
                margin = (noise_floor - 0.4) / 0.4
            elif signal_type == "periodic":
                margin = (periodicity - 0.3) / 0.3
            else:  # transient
                margin = (entropy_delta_abs - 2.0) / 2.0
            confidence = max(min(0.5 + margin * 0.5, 1.0), 0.3)
            components = []
        else:
            signal_type = "complex"
            components = triggered
            confidence = max(0.3, 0.5)

        return {
            "signal_type": signal_type,
            "confidence": confidence,
            "components": components,
        }

    def repair_check(self, state: SystemState) -> bool:
        report = state.get("signal_report")
        if report is None:
            return False
        features = report.get("features")
        if features is None:
            return False
        # Verify all feature values are finite.
        for key in ("density", "entropy", "coherence", "periodicity", "noise_floor", "impedance", "bigram_entropy"):
            val = features.get(key)
            if val is None or not math.isfinite(val):
                return False
        # Verify signal_type is valid.
        classification = report.get("classification")
        if classification is None:
            return False
        valid_types = {"steady_state", "transient", "periodic", "noise", "complex"}
        if classification.get("signal_type") not in valid_types:
            return False
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return self._consecutive_none_count >= 3
