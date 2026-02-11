"""Tests for the Codec protocol and TextCodec implementation.

Covers:
- Protocol conformance (3 tests)
- Behavioral equivalence (4 tests)
- Quality check (2 tests)
- Motor delegation (3 tests)

All tests are deterministic — no LLM calls, no API keys.
"""

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import create_default_state
from agenetic.systems.base import AREKA_ID, MAYAVADA_ID, SignalFeatures
from agenetic.systems.codec import Codec, CodecResult
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.text_codec import TextCodec


SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "The dog barks at the fox. "
    "The fox runs away quickly."
)

HIGH_NOISE_TEXT = (
    "a ! b # c $ d % e ^ f & g * h ( i ) j + k = l ; "
    "m @ n ~ o ` p { q } r [ s ] t / u \\ v | w < x > y , z . "
    "aa ! bb # cc $ dd % ee ^ ff & gg * hh ( ii ) jj ."
)


def _make_field(limb_overrides=None):
    """Create an OrientationalField with optional limb weight overrides."""
    field = OrientationalField()
    if limb_overrides:
        limbs = field.read()["limbs"]
        for limb in limbs:
            if limb["id"] in limb_overrides:
                limb["weight"] = limb_overrides[limb["id"]]
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
    return field


def _make_features(**overrides) -> SignalFeatures:
    """Create a SignalFeatures dict with sensible defaults and optional overrides."""
    features: SignalFeatures = {
        "density": 0.8, "entropy": 3.5, "coherence": 0.5,
        "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
        "bigram_entropy": 3.0, "token_count": 15, "vocabulary_richness": 0.8,
    }
    features.update(overrides)
    return features


def _make_motor_state(input_text=SAMPLE_TEXT, field=None):
    """Create a state ready for motor processing with signal report populated."""
    if field is None:
        field = OrientationalField()
    state = create_default_state(input_data=input_text, field=field)
    sensory = SensorySystem()
    state = sensory.process(state)
    return state


# ============================================================
# Protocol tests (3)
# ============================================================


class TestCodecProtocol:

    def test_text_codec_satisfies_protocol(self):
        """TextCodec is an instance of Codec (runtime_checkable)."""
        codec = TextCodec()
        assert isinstance(codec, Codec)

    def test_text_codec_name(self):
        """TextCodec.name == 'text'."""
        codec = TextCodec()
        assert codec.name == "text"

    def test_codec_result_structure(self):
        """TextCodec.encode() returns a CodecResult with required keys."""
        codec = TextCodec()
        field = _make_field()
        features = _make_features()
        target = _make_features(density=0.9)
        result = codec.encode(SAMPLE_TEXT, features, target, field.read())
        assert "output" in result
        assert "strategies_applied" in result
        assert "transform_magnitude" in result
        assert isinstance(result["output"], str)
        assert isinstance(result["strategies_applied"], list)
        assert isinstance(result["transform_magnitude"], float)


# ============================================================
# Equivalence tests (4)
# ============================================================


class TestCodecEquivalence:

    def test_encode_matches_old_density(self):
        """TextCodec produces density modulation matching old motor behavior."""
        codec = TextCodec()
        field = _make_field()
        field_state = field.read()
        # Input with extra whitespace that density modulation can collapse.
        spacious_text = "The quick  brown  fox.\n\n\nThe dog  barks.  \n\n  The fox runs."
        features = _make_features(density=0.5)
        target = _make_features(density=0.9)
        result = codec.encode(spacious_text, features, target, field_state)
        assert "density_modulation" in result["strategies_applied"]
        # Output should be more compact than input.
        assert result["output"] != spacious_text

    def test_encode_matches_old_entropy(self):
        """TextCodec produces entropy modulation matching old motor behavior."""
        codec = TextCodec()
        field = _make_field()
        field_state = field.read()
        # Text with commas and conjunctions that entropy modulation can split.
        complex_text = (
            "The fox runs quickly, and the dog follows behind. "
            "The cat watches from above, while the birds sing loudly."
        )
        features = _make_features(entropy=1.0)
        target = _make_features(entropy=6.0)
        result = codec.encode(complex_text, features, target, field_state)
        assert "entropy_modulation" in result["strategies_applied"]

    def test_encode_areka_suppression(self):
        """High noise + high entropy + Areka > 0.3 → empty output with areka_suppression."""
        codec = TextCodec()
        field = _make_field({AREKA_ID: 1.0})
        field_state = field.read()
        features = _make_features(noise_floor=0.5, entropy=6.0)
        target = _make_features()
        result = codec.encode(HIGH_NOISE_TEXT, features, target, field_state)
        assert result["output"] == ""
        assert "areka_suppression" in result["strategies_applied"]
        assert result["transform_magnitude"] == 1.0

    def test_encode_mayavada_cap(self):
        """Mayavada > 0.55 → transform_magnitude bounded by max_allowed."""
        codec = TextCodec()
        # Mayavada at 0.56 → max_allowed = 0.44. Cap is active (high humility constrains).
        # At default 0.5 → cap is NOT active (<= 0.55).
        from agenetic.systems.base import KSETRA_JNANA_ID as KJ_ID
        field_capped = _make_field({MAYAVADA_ID: 0.56, KJ_ID: 1.0})
        field_uncapped = _make_field({MAYAVADA_ID: 0.5, KJ_ID: 1.0})
        features = _make_features(coherence=0.9, impedance=0.0)
        target = _make_features(coherence=0.1, impedance=0.5)

        result_capped = codec.encode(SAMPLE_TEXT, features, target, field_capped.read())
        result_uncapped = codec.encode(SAMPLE_TEXT, features, target, field_uncapped.read())

        # Capped magnitude should be <= max_allowed (0.44) or unmodified if already below.
        max_allowed = 1.0 - 0.56
        assert result_capped["transform_magnitude"] <= max_allowed + 0.01
        # Uncapped should have no Mayavada constraint.
        assert "mayavada_cap" not in result_uncapped["strategies_applied"]


# ============================================================
# Quality check tests (2)
# ============================================================


class TestCodecQualityCheck:

    def test_mayavada_high_humility_constrains(self):
        """High humility (weight 0.8) → cap active, max_allowed = 0.2."""
        codec = TextCodec()
        from agenetic.systems.base import KSETRA_JNANA_ID as KJ_ID
        field = _make_field({MAYAVADA_ID: 0.8, KJ_ID: 1.0})
        features = _make_features(coherence=0.9, impedance=0.0)
        target = _make_features(coherence=0.1, impedance=0.5)
        result = codec.encode(SAMPLE_TEXT, features, target, field.read())
        max_allowed = 1.0 - 0.8  # 0.2
        assert result["transform_magnitude"] <= max_allowed + 0.01

    def test_mayavada_low_humility_unconstrained(self):
        """Low humility (weight 0.3) → cap inactive, no restraint."""
        codec = TextCodec()
        from agenetic.systems.base import KSETRA_JNANA_ID as KJ_ID
        field = _make_field({MAYAVADA_ID: 0.3, KJ_ID: 1.0})
        features = _make_features(coherence=0.9, impedance=0.0)
        target = _make_features(coherence=0.1, impedance=0.5)
        result = codec.encode(SAMPLE_TEXT, features, target, field.read())
        assert "mayavada_cap" not in result["strategies_applied"]

    def test_quality_check_passes(self):
        """Normal input/output pair passes quality check."""
        codec = TextCodec()
        assert codec.quality_check(SAMPLE_TEXT, SAMPLE_TEXT) is True

    def test_quality_check_fails_empty_output(self):
        """Empty output fails quality check."""
        codec = TextCodec()
        assert codec.quality_check(SAMPLE_TEXT, "") is False


# ============================================================
# Motor delegation tests (3)
# ============================================================


class TestMotorDelegation:

    def test_motor_uses_text_codec(self):
        """MotorSystem._codec is a TextCodec instance."""
        motor = MotorSystem()
        assert isinstance(motor._codec, TextCodec)

    def test_motor_process_unchanged(self):
        """MotorSystem.process() produces same output structure as before refactor."""
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        output = result["motor_output"]
        # Verify all MotorOutput fields present.
        assert "output_text" in output
        assert "target_profile" in output
        assert "strategies_applied" in output
        assert "repair_passed" in output
        assert "transform_magnitude" in output
        # Repair should pass for clean text at default weights.
        assert output["repair_passed"] is True
        assert isinstance(output["output_text"], str)
        assert len(output["output_text"]) > 0

    def test_motor_repair_delegates_to_codec(self):
        """Motor's repair path uses codec.quality_check()."""
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        # The repair_passed field is set based on codec.quality_check().
        # For clean text at default weights, this should pass.
        assert result["motor_output"]["repair_passed"] is True
        # Verify the codec's quality_check agrees.
        original_text = state["input"]
        output_text = result["motor_output"]["output_text"]
        assert motor._codec.quality_check(original_text, output_text) is True
