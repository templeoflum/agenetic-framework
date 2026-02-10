"""Codec protocol — interface for motor output encoding.

A Codec transforms input data toward a target signal profile.
TextCodec is the first implementation (text restructuring).
Future codecs could handle audio, visual, or other modalities.
"""

from __future__ import annotations

from typing import Protocol, TypedDict, runtime_checkable

from agenetic.systems.base import SignalFeatures


class CodecResult(TypedDict):
    """Result of a codec encode operation."""

    output: str
    strategies_applied: list[str]
    transform_magnitude: float


@runtime_checkable
class Codec(Protocol):
    """Protocol for motor output codecs.

    A codec takes input data, current signal features, a target profile,
    and field state, then produces transformed output with metadata.
    """

    @property
    def name(self) -> str:
        """Codec identifier (e.g., 'text', 'audio')."""
        ...

    def encode(
        self,
        input_data: str,
        current_features: SignalFeatures,
        target_profile: SignalFeatures,
        field_state: dict,
    ) -> CodecResult:
        """Transform input toward target profile.

        Returns CodecResult with transformed output and metadata.
        """
        ...

    def quality_check(self, original: str, output: str) -> bool:
        """Verify output preserves content adequately."""
        ...
