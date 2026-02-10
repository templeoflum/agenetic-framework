# 013 — Motor Codec Refactor

Date: 2026-02-10
Directive type: Pure refactor (zero behavior change, no new features)

## What This Directive Does

Extracts motor's ~450 LOC of text restructuring logic into a TextCodec class behind a Codec protocol. MotorSystem becomes an orchestrator: reads field, computes target, delegates to codec, checks quality, tracks apoptotic state. The codec does the actual text transformation.

This is the safest directive in the conscious-layer sequence. No behavior changes. Every existing test passes unchanged. The value is structural: motor gains a codec interface before Directive 014 adds ConsciousOutput consumption.

## Design Decisions and Rationale

### Why extract now, not during 014?

014 will add ConsciousOutput consumption — motor will need to render semantic decisions into signal-level output. That's a behavior change. Mixing a behavior change with a structural refactor in the same directive makes review harder and failures ambiguous. Extract first (013), then add behavior (014). Each directive has one job.

### Codec protocol mirrors Deliberator protocol

Both use `runtime_checkable` Protocol from typing. Both are structural (any class satisfying the interface works). Both have a primary method (encode/deliberate) and a quality method (quality_check/repair_check concept).

This isn't accidental — it's the same pattern. The conscious layer has a protocol for meaning construction (Deliberator). The motor layer has a protocol for output encoding (Codec). Both are swappable. Both have mock and real implementations.

### What moves vs what stays

**Moves to TextCodec:**
- All 6 modulation functions (these ARE text restructuring)
- Transform magnitude computation (measuring text changes)
- Blend-toward-original (Māyāvāda blending is text-specific)
- Quality check (checking text preservation)
- Ārēka suppression gate (operates on text signal features)
- Māyāvāda cap (operates on text transformation)
- Svadharma/Kṣetra-Jñāna scaling (modifies strategy thresholds)

**Stays in MotorSystem:**
- Field reading and target profile computation
- Input coercion (_to_str)
- Empty input handling
- Current features extraction from signal report
- MotorOutput construction
- Repair failure tracking (_consecutive_repair_failures)
- Apoptotic condition check

The principle: MotorSystem owns the "when" and "what" (when to encode, what context to provide). TextCodec owns the "how" (how to transform text toward a target profile).

### CodecResult vs MotorOutput

TextCodec.encode() returns CodecResult (output, strategies_applied, transform_magnitude). MotorSystem wraps this into MotorOutput (adds target_profile, repair_passed). The codec doesn't know about repair — that's orchestration. The codec doesn't know about target_profile as an output field — it receives the target as input.

### Why 12 tests, not more?

The 102 existing motor tests (58 unit + 44 round-trip) ARE the behavioral equivalence tests. If the refactor changes any behavior, those tests catch it. The 12 new tests verify structural properties: protocol conformance, delegation, and a few key equivalence spot-checks. Adding more equivalence tests is redundant — the existing suite already covers the behavior surface exhaustively.

## Broader Roadmap (011–017)

011 ✓ ConsciousOutput type, gate, Deliberator protocol, first implementation. 262 tests.
012 ✓ Prompt assembly refinement. Graduated intensity, limb interactions, observation harness. 292 tests.
013 — **This directive.** Motor codec refactor. TextCodec extraction. Zero behavior change.
014 — Integration. Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path.
015 — Mechanical audit. DNAgent reads everything, reports raw. Zero code changes.
016 — Conceptual audit. Fresh planning instance, adversarial posture.
017 — Remediation.

## What to Watch

- **Import cycles.** TextCodec imports from base.py (SignalFeatures, limb ID constants, compute_target_profile). MotorSystem imports TextCodec. Make sure no circular imports emerge.

- **Private function visibility.** The 6 modulation functions are module-level in text_codec.py (not methods). Tests in test_motor.py don't import them directly — they test through MotorSystem.process(). If any test_motor.py test imports a private function from motor.py that was moved, it will break. Check test imports carefully.

- **_to_str stays in motor.** It handles None, non-string inputs. The codec receives already-coerced string input. If _to_str accidentally moves to the codec, motor's empty-input handling might break.
