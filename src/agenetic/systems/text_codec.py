"""Text restructuring codec — signal-level text transformation.

Implements the Codec protocol for text output. Restructures text toward
target signal profiles using six feature modulation strategies, governed
by Areka suppression, Mayavada cap, Svadharma threshold scaling, and
Ksetra-Jnana delta scaling.

This is a pure extraction from MotorSystem.process() — identical behavior,
new home. All functions are unchanged from motor.py.
"""

from __future__ import annotations

import re
from collections import Counter

from agenetic.systems.base import (
    AREKA_ID,
    KSETRA_JNANA_ID,
    MAYAVADA_ID,
    SignalFeatures,
    SVADHARMA_ID,
    get_limb_weight as _get_limb_weight,
)
from agenetic.systems.codec import CodecResult


# ============================================================
# Restructuring strategies (moved from motor.py, unchanged)
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
    """Adjust vocabulary entropy toward target using sentence-level restructuring.

    Higher entropy = more structural variety (split sentences, vary openings).
    Lower entropy = more uniformity (merge short sentences, normalize length).

    Sentence-level approach preserves more original tokens than token-level
    replacement, making the repair check easier to satisfy.
    """
    if not text:
        return text

    tokens = text.split()
    if len(tokens) < 2:
        return text

    delta = target - current
    if abs(delta) < 0.5:
        return text

    # Split into sentences preserving terminators.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
        return text

    if delta > 0:
        # Increase entropy: split longer sentences at conjunctions/commas
        # to create more structural variety.
        result = []
        conjunctions = {'and', 'but', 'or', 'yet', 'so', 'while', 'when',
                        'because', 'although', 'which', 'where', 'that'}
        for sent in sentences:
            # Try splitting at commas first.
            comma_parts = sent.split(', ')
            if len(comma_parts) >= 2:
                # Turn comma-separated clauses into separate sentences.
                for j, part in enumerate(comma_parts):
                    part = part.strip()
                    if not part:
                        continue
                    # Capitalize first word of new sentence.
                    part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
                    # Add period if the part doesn't end with punctuation.
                    if part and part[-1] not in '.!?':
                        part += '.'
                    result.append(part)
            else:
                # Try splitting at conjunctions.
                words = sent.split()
                split_indices = [i for i, w in enumerate(words)
                                 if w.lower().rstrip('.,;:') in conjunctions and i > 1]
                if split_indices:
                    idx = split_indices[0]
                    first_part = ' '.join(words[:idx]).rstrip('.,;:')
                    if first_part and first_part[-1] not in '.!?':
                        first_part += '.'
                    second_part = ' '.join(words[idx + 1:])
                    if second_part:
                        second_part = second_part[0].upper() + second_part[1:] if len(second_part) > 1 else second_part.upper()
                        if second_part[-1] not in '.!?':
                            second_part += '.'
                        result.append(first_part)
                        result.append(second_part)
                    else:
                        result.append(sent)
                else:
                    result.append(sent)
        return ' '.join(result)
    else:
        # Decrease entropy: merge short sentences with connectives
        # to create more uniform structure.
        connectives = ['and', 'which', 'where', 'while']
        result = []
        i = 0
        while i < len(sentences):
            current_sent = sentences[i].rstrip()
            # If next sentence exists and current is short, merge them.
            if (i + 1 < len(sentences)
                    and len(current_sent.split()) <= 8):
                # Strip terminal punctuation from first sentence for merging.
                merged_first = current_sent.rstrip('.!?')
                connective = connectives[i % len(connectives)]
                next_sent = sentences[i + 1].strip()
                # Lowercase the start of the merged second sentence.
                if next_sent and next_sent[0].isupper():
                    next_sent = next_sent[0].lower() + next_sent[1:]
                merged = f"{merged_first} {connective} {next_sent}"
                result.append(merged)
                i += 2
            else:
                result.append(current_sent)
                i += 1
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
# Transformation measurement and blending (moved from motor.py)
# ============================================================


def _compute_transform_magnitude(original: str, output: str) -> float:
    """Measure how much output deviated from original (0.0-1.0).

    Returns 1.0 - token_overlap_ratio. At 0.0, output is identical.
    At 1.0, no tokens overlap.
    """
    if not original or not output:
        return 1.0 if original != output else 0.0
    orig_tokens = original.lower().split()
    out_tokens = output.lower().split()
    if not orig_tokens:
        return 0.0
    orig_set = set(orig_tokens)
    out_set = set(out_tokens)
    overlap = len(orig_set & out_set) / len(orig_set)
    return 1.0 - overlap


def _blend_toward_original(
    original: str, output: str, max_allowed: float, current_magnitude: float
) -> str:
    """Blend output back toward original to respect Mayavada cap.

    Takes proportional mix of original tokens and output tokens.
    """
    orig_tokens = original.split()
    out_tokens = output.split()
    if not orig_tokens or not out_tokens:
        return original

    # Compute blend ratio: how much of the output to keep.
    # If max_allowed is 0.2 and current_magnitude is 0.5,
    # keep 0.2/0.5 = 40% of output changes.
    blend_ratio = max_allowed / current_magnitude if current_magnitude > 0 else 0.0
    blend_ratio = min(max(blend_ratio, 0.0), 1.0)

    # Use the shorter length to avoid index errors.
    min_len = min(len(orig_tokens), len(out_tokens))
    result = []
    for i in range(min_len):
        if orig_tokens[i] == out_tokens[i]:
            result.append(orig_tokens[i])
        else:
            # Keep output token for the first blend_ratio fraction of changes.
            # Deterministic: count how many changes we've seen so far.
            changes_before = sum(
                1 for j in range(i) if j < len(orig_tokens) and j < len(out_tokens)
                and orig_tokens[j] != out_tokens[j]
            )
            total_changes = sum(
                1 for j in range(min_len)
                if orig_tokens[j] != out_tokens[j]
            )
            if total_changes > 0 and changes_before < int(total_changes * blend_ratio):
                result.append(out_tokens[i])
            else:
                result.append(orig_tokens[i])

    # Append remaining tokens from whichever is longer, blended.
    if len(out_tokens) > min_len and blend_ratio > 0.5:
        result.extend(out_tokens[min_len:])
    elif len(orig_tokens) > min_len:
        result.extend(orig_tokens[min_len:])

    return ' '.join(result)


# ============================================================
# TextCodec class
# ============================================================


class TextCodec:
    """Text restructuring codec — signal-level text transformation.

    Implements the Codec protocol for text output. Restructures text
    toward target signal profiles using six feature modulation strategies,
    governed by Areka suppression, Mayavada cap, Svadharma threshold
    scaling, and Ksetra-Jnana delta scaling.

    This is a pure extraction from MotorSystem.process() — identical
    behavior, new home.
    """

    @property
    def name(self) -> str:
        return "text"

    def encode(
        self,
        input_data: str,
        current_features: SignalFeatures,
        target_profile: SignalFeatures,
        field_state: dict,
    ) -> CodecResult:
        """Apply text restructuring strategies toward target profile."""
        text = input_data

        # --- Ārēka suppression gate ---
        # Ārēka defense-in-depth: codec threshold (0.3) is lower than conscious gate (0.7)
        # because this is the final output gate — more cautious by design.
        # See also: conscious.py Ārēka gate path.
        areka_w = _get_limb_weight(field_state, AREKA_ID)
        if areka_w > 0.3:
            input_noise = current_features["noise_floor"]
            input_entropy = current_features["entropy"]
            if input_noise > 0.3 and input_entropy > 5.0:
                return {
                    "output": "",
                    "strategies_applied": ["areka_suppression"],
                    "transform_magnitude": 1.0,
                }

        # --- Svadharma threshold scaling and Ksetra-Jnana delta scaling ---
        svadharma_w = _get_limb_weight(field_state, SVADHARMA_ID)
        threshold_scale = 0.5 + svadharma_w  # At 1.0: 1.5x; at 0.0: 0.5x
        ksetra_w = _get_limb_weight(field_state, KSETRA_JNANA_ID)
        delta_scale = 0.5 + ksetra_w * 0.5   # At 1.0: 1.0; at 0.0: 0.5

        # Apply strategies in order. Track which fired.
        strategies: list[str] = []
        output = text

        # Strategy thresholds (base values, scaled by Svadharma).
        density_thresh = 0.05 * threshold_scale
        entropy_thresh = 0.5 * threshold_scale
        coherence_thresh = 0.1 * threshold_scale
        impedance_thresh = 0.05 * threshold_scale
        periodicity_thresh = 0.05 * threshold_scale
        noise_thresh = 0.05 * threshold_scale

        # 1. Density modulation (mean weight).
        density_delta = (target_profile["density"] - current_features["density"]) * delta_scale
        prev = output
        output = _modulate_density(output, current_features["density"] + density_delta, current_features["density"])
        if output != prev:
            strategies.append("density_modulation")

        # 2. Entropy modulation (Tarka) — sentence-level.
        entropy_delta = (target_profile["entropy"] - current_features["entropy"]) * delta_scale
        prev = output
        adjusted_entropy_target = current_features["entropy"] + entropy_delta
        if abs(entropy_delta) >= entropy_thresh:
            output = _modulate_entropy(output, adjusted_entropy_target, current_features["entropy"])
        if output != prev:
            strategies.append("entropy_modulation")

        # 3. Coherence modulation (Samatvam).
        coherence_delta = (target_profile["coherence"] - current_features["coherence"]) * delta_scale
        prev = output
        if abs(coherence_delta) >= coherence_thresh:
            output = _modulate_coherence(
                output, current_features["coherence"] + coherence_delta, current_features["coherence"]
            )
        if output != prev:
            strategies.append("coherence_modulation")

        # 4. Impedance modulation (Nivrtti).
        impedance_delta = (target_profile["impedance"] - current_features["impedance"]) * delta_scale
        prev = output
        if abs(impedance_delta) >= impedance_thresh:
            output = _modulate_impedance(
                output, current_features["impedance"] + impedance_delta, current_features["impedance"]
            )
        if output != prev:
            strategies.append("impedance_modulation")

        # 5. Periodicity modulation (Prakasa).
        periodicity_delta = (target_profile["periodicity"] - current_features["periodicity"]) * delta_scale
        prev = output
        if abs(periodicity_delta) >= periodicity_thresh:
            output = _modulate_periodicity(
                output, current_features["periodicity"] + periodicity_delta, current_features["periodicity"]
            )
        if output != prev:
            strategies.append("periodicity_modulation")

        # 6. Noise floor modulation (Sraddha).
        noise_delta = (target_profile["noise_floor"] - current_features["noise_floor"]) * delta_scale
        prev = output
        if abs(noise_delta) >= noise_thresh:
            output = _modulate_noise_floor(
                output, current_features["noise_floor"] + noise_delta, current_features["noise_floor"]
            )
        if output != prev:
            strategies.append("noise_floor_modulation")

        # --- Mayavada transformation cap ---
        mayavada_w = _get_limb_weight(field_state, MAYAVADA_ID)
        transform_magnitude = _compute_transform_magnitude(text, output)

        if mayavada_w > 0.55:
            max_allowed = 1.0 - mayavada_w
            if transform_magnitude > max_allowed and max_allowed > 0.0:
                output = _blend_toward_original(text, output, max_allowed, transform_magnitude)
                strategies.append("mayavada_cap")
                transform_magnitude = _compute_transform_magnitude(text, output)
            elif max_allowed == 0.0:
                output = text
                strategies.append("mayavada_cap")
                transform_magnitude = 0.0

        return {
            "output": output,
            "strategies_applied": strategies,
            "transform_magnitude": transform_magnitude,
        }

    def quality_check(self, original: str, output: str) -> bool:
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
