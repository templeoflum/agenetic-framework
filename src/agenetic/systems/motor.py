"""Motor/Output system — Signal-level text restructuring engine.

Relationship to information: Translates. Converts internal states into
appropriate external form.

Operates at the signal level: restructures text structurally to match target
signal profiles derived from orientational field limb weights. No LLM calls,
no semantic interpretation. Pure Python computation.

Serves dual purpose: output encoding AND calibration instrument for testing
limb-to-feature mappings via motor->sensory round-trip feedback loops.

Tick rate: On demand -- fires on both reflex path and post-conscious path.

Uses only Python stdlib -- deterministic given same input + field state.
"""

from __future__ import annotations

import re
from collections import Counter

from agenetic.systems.base import (
    BaseSystem,
    MotorOutput,
    SignalFeatures,
    SystemState,
)

# Limb IDs that govern specific strategies.
PRAKASA_ID = 1     # Periodicity modulation (inverse: more Prakasa = less forced pattern)
TARKA_ID = 2       # Entropy modulation (more Tarka = more variety)
NIVRTTI_ID = 3     # Impedance modulation (inverse: more Nivrtti = simpler output)
SAMATVAM_ID = 7    # Coherence modulation (more Samatvam = more coherent)


def _get_limb_weight(field_state, limb_id: int) -> float:
    """Get a specific limb weight from the field state."""
    limbs = field_state.get("limbs", [])
    for limb in limbs:
        if limb["id"] == limb_id:
            return limb["weight"]
    return 1.0


def _mean_weight(field_state) -> float:
    """Compute mean of all limb weights."""
    limbs = field_state.get("limbs", [])
    if not limbs:
        return 1.0
    return sum(limb["weight"] for limb in limbs) / len(limbs)


def _to_str(input_data) -> str:
    """Convert any input to string representation."""
    if input_data is None:
        return ""
    if isinstance(input_data, str):
        return input_data
    return str(input_data)


def _compute_target_profile(field_state) -> SignalFeatures:
    """Compute target signal features from orientational field weights.

    Each target is derived from the governing limb weight(s).
    With default weights (all 1.0), produces moderate targets:
    density=0.8, entropy=3.5, coherence=0.7, impedance=0.0,
    periodicity=0.0, noise_floor=0.0.
    """
    mean_w = _mean_weight(field_state)
    tarka_w = _get_limb_weight(field_state, TARKA_ID)
    samatvam_w = _get_limb_weight(field_state, SAMATVAM_ID)
    nivrtti_w = _get_limb_weight(field_state, NIVRTTI_ID)
    prakasa_w = _get_limb_weight(field_state, PRAKASA_ID)

    return {
        "density": min(max(mean_w * 0.8, 0.0), 1.0),
        "entropy": max(tarka_w * 3.5, 0.0),
        "coherence": min(max(samatvam_w * 0.7, 0.0), 1.0),
        "periodicity": min(max((1.0 - prakasa_w) * 0.3, 0.0), 1.0),
        "noise_floor": min(max((1.0 - mean_w) * 0.3, 0.0), 1.0),
        "impedance": min(max((1.0 - nivrtti_w) * 0.3, 0.0), 1.0),
        "token_count": 0,            # not directly targeted
        "vocabulary_richness": 0.0,   # derived from entropy strategy
    }


# ============================================================
# Restructuring strategies
# ============================================================


def _modulate_density(text: str, target: float, current: float) -> str:
    """Adjust text density toward target.

    Higher density = more compact (collapse whitespace).
    Lower density = more spacious (add spacing).
    """
    if not text:
        return text

    delta = target - current
    if abs(delta) < 0.05:
        return text

    if delta > 0:
        # Increase density: collapse multiple whitespace to single space.
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()
    else:
        # Decrease density: add spacing between sentences.
        text = re.sub(r'([.!?])\s*', r'\1\n\n', text)

    return text


def _modulate_entropy(text: str, target: float, current: float) -> str:
    """Adjust vocabulary entropy toward target.

    Higher entropy = more varied vocabulary (deduplicate repeated tokens).
    Lower entropy = more constrained vocabulary (homogenize rare tokens).
    """
    if not text:
        return text

    tokens = text.split()
    if len(tokens) < 2:
        return text

    delta = target - current
    if abs(delta) < 0.5:
        return text

    if delta > 0:
        # Increase entropy: make repeated tokens unique by appending
        # occurrence index (deterministic, reversible labeling).
        counts: dict[str, int] = {}
        result = []
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
            if counts[token] > 1:
                result.append(f"{token}-{counts[token]}")
            else:
                result.append(token)
        return ' '.join(result)
    else:
        # Decrease entropy: replace a fraction of rare tokens with the
        # most common token. Capped at 30% of singletons to preserve
        # content for repair check.
        freq = Counter(tokens)
        most_common = freq.most_common(1)[0][0]
        singletons = [i for i, t in enumerate(tokens)
                       if freq[t] == 1 and t != most_common and i > 0]
        max_replacements = max(1, len(singletons) // 3)
        result = list(tokens)
        replaced = 0
        for idx in singletons:
            if replaced >= max_replacements:
                break
            result[idx] = most_common
            replaced += 1
        return ' '.join(result)


def _modulate_coherence(text: str, target: float, current: float) -> str:
    """Adjust sentence-to-sentence coherence toward target.

    Higher coherence = sentences share more vocabulary (bridge words).
    Lower coherence = more disjoint (reverse sentence order).
    """
    if not text:
        return text

    delta = target - current
    if abs(delta) < 0.1:
        return text

    # Split into sentences preserving terminators.
    parts = re.split(r'(?<=[.!?])\s+', text)
    if len(parts) < 2:
        return text

    if delta > 0:
        # Increase coherence: carry the last content word of each sentence
        # into the start of the next sentence.
        result = [parts[0]]
        for i in range(1, len(parts)):
            prev_words = re.findall(r'[a-zA-Z]+', parts[i - 1])
            bridge = prev_words[-1] if prev_words else ''
            current_words = parts[i].split()
            if bridge and current_words and current_words[0].lower() != bridge.lower():
                result.append(bridge + ' ' + parts[i])
            else:
                result.append(parts[i])
        return ' '.join(result)
    else:
        # Decrease coherence: reverse sentence order.
        parts.reverse()
        return ' '.join(parts)


def _modulate_impedance(text: str, target: float, current: float) -> str:
    """Adjust structural impedance toward target.

    Lower impedance = simpler structure (strip non-ASCII, brackets).
    Higher impedance = more structure (add section markers).
    """
    if not text:
        return text

    delta = target - current
    if abs(delta) < 0.05:
        return text

    if delta < 0:
        # Decrease impedance: simplify structure.
        text = ''.join(c if ord(c) < 128 else '' for c in text)
        text = re.sub(r'[{}\[\]()]', '', text)
        text = re.sub(r' +', ' ', text).strip()
    else:
        # Increase impedance: add bracketed section markers.
        parts = re.split(r'(?<=[.!?])\s+', text)
        result = []
        for i, part in enumerate(parts):
            if part.strip():
                result.append(f"[{i + 1}] {part}")
        text = ' '.join(result)

    return text


def _modulate_periodicity(text: str, target: float, current: float) -> str:
    """Adjust bigram repetition toward target.

    Lower periodicity = break repeated bigrams (insert separators).
    Higher periodicity = repeat key phrases at intervals.
    """
    if not text:
        return text

    tokens = text.split()
    if len(tokens) < 3:
        return text

    delta = target - current
    if abs(delta) < 0.05:
        return text

    if delta < 0:
        # Decrease periodicity: insert separator between repeated bigrams.
        bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
        bg_counts = Counter(bigrams)
        seen: set[tuple[str, str]] = set()
        result = [tokens[0]]
        for i in range(len(tokens) - 1):
            bg = (tokens[i], tokens[i + 1])
            if bg_counts[bg] > 1 and bg in seen:
                result.append('--')
            seen.add(bg)
            result.append(tokens[i + 1])
        return ' '.join(result)
    else:
        # Increase periodicity: repeat last two tokens at regular intervals.
        phrase = tokens[-2:]
        interval = max(3, len(tokens) // 3)
        result = []
        for i, t in enumerate(tokens):
            result.append(t)
            if (i + 1) % interval == 0 and i < len(tokens) - 1:
                result.extend(phrase)
        return ' '.join(result)


def _modulate_noise_floor(text: str, target: float, current: float) -> str:
    """Adjust noise floor (proportion of low-information tokens) toward target.

    Lower noise = remove single-char and punctuation-only tokens.
    Higher noise = add structural punctuation markers.
    """
    if not text:
        return text

    tokens = text.split()
    if not tokens:
        return text

    delta = target - current
    if abs(delta) < 0.05:
        return text

    if delta < 0:
        # Decrease noise: remove single-char non-alphanumeric and
        # pure-punctuation tokens.
        result = []
        for t in tokens:
            if len(t) == 1 and not t.isalnum():
                continue
            if len(t) > 1 and all(not c.isalnum() for c in t):
                continue
            result.append(t)
        return ' '.join(result) if result else text
    else:
        # Increase noise: insert marker characters between sentences.
        parts = re.split(r'(?<=[.!?])\s+', text)
        return ' | '.join(parts)


# ============================================================
# Motor system
# ============================================================


class MotorSystem(BaseSystem):
    """Signal-level text restructuring engine.

    Reverse transduction: where sensory extracts signal features FROM text,
    motor adjusts text TO target signal profiles shaped by the orientational
    field. Six restructuring strategies, each governed by specific limb weights.

    Deterministic given the same input + field state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="motor",
            description="Restructures text toward target signal profiles shaped by orientational field weights",
        )
        self._consecutive_repair_failures = 0

    @property
    def tick_rate(self) -> str:
        return "on_demand"

    def process(self, state: SystemState) -> SystemState:
        raw_input = state["input"]
        field_state = state["field"]
        signal_report = state.get("signal_report")

        text = _to_str(raw_input)

        # Compute target profile from field weights.
        target = _compute_target_profile(field_state)

        # Handle empty/None input.
        if not text:
            motor_output: MotorOutput = {
                "output_text": "",
                "target_profile": target,
                "strategies_applied": [],
                "repair_passed": True,
            }
            return {**state, "motor_output": motor_output}

        # Get current features from signal report (if available).
        if signal_report is not None:
            current = signal_report["features"]
        else:
            # No signal report -- use neutral defaults.
            current: SignalFeatures = {
                "density": 0.5, "entropy": 2.0, "coherence": 0.5,
                "periodicity": 0.0, "noise_floor": 0.0, "impedance": 0.0,
                "token_count": len(text.split()), "vocabulary_richness": 0.5,
            }

        # Apply strategies in order. Track which fired.
        strategies: list[str] = []
        output = text

        # 1. Density modulation (mean weight).
        prev = output
        output = _modulate_density(output, target["density"], current["density"])
        if output != prev:
            strategies.append("density_modulation")

        # 2. Entropy modulation (Tarka).
        prev = output
        output = _modulate_entropy(output, target["entropy"], current["entropy"])
        if output != prev:
            strategies.append("entropy_modulation")

        # 3. Coherence modulation (Samatvam).
        prev = output
        output = _modulate_coherence(output, target["coherence"], current["coherence"])
        if output != prev:
            strategies.append("coherence_modulation")

        # 4. Impedance modulation (Nivrtti).
        prev = output
        output = _modulate_impedance(output, target["impedance"], current["impedance"])
        if output != prev:
            strategies.append("impedance_modulation")

        # 5. Periodicity modulation (Prakasa).
        prev = output
        output = _modulate_periodicity(output, target["periodicity"], current["periodicity"])
        if output != prev:
            strategies.append("periodicity_modulation")

        # 6. Noise floor modulation (mean weight).
        prev = output
        output = _modulate_noise_floor(output, target["noise_floor"], current["noise_floor"])
        if output != prev:
            strategies.append("noise_floor_modulation")

        # Repair check: verify output preserves content adequately.
        repair_passed = self._check_output_quality(text, output)

        if not repair_passed:
            self._consecutive_repair_failures += 1
            # Fall back to original text on repair failure.
            output = text
            strategies = ["fallback_to_original"]
        else:
            self._consecutive_repair_failures = 0

        motor_output = {
            "output_text": output,
            "target_profile": target,
            "strategies_applied": strategies,
            "repair_passed": repair_passed,
        }

        return {**state, "motor_output": motor_output}

    def _check_output_quality(self, original: str, output: str) -> bool:
        """Check that restructuring preserved content adequately.

        Verifies output is non-empty, length ratio is within bounds,
        and sufficient token overlap exists with the original.
        """
        if not output or not output.strip():
            return False

        # Length ratio check: output shouldn't be > 3x or < 0.2x original.
        orig_len = len(original)
        out_len = len(output)
        if orig_len > 0:
            ratio = out_len / orig_len
            if ratio > 3.0 or ratio < 0.2:
                return False

        # Token overlap check: at least 20% of original tokens should survive.
        orig_tokens = set(original.lower().split())
        out_tokens = set(output.lower().split())
        if orig_tokens:
            overlap = len(orig_tokens & out_tokens) / len(orig_tokens)
            if overlap < 0.2:
                return False

        return True

    def repair_check(self, state: SystemState) -> bool:
        motor_output = state.get("motor_output")
        if motor_output is None:
            return False
        return motor_output.get("repair_passed", False)

    def apoptotic_condition(self, state: SystemState) -> bool:
        if state["input"] is None:
            return True
        return self._consecutive_repair_failures >= 3
