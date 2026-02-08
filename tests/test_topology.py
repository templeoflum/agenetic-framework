"""Tests for network topology.

Verifies the connection matrix matches the architecture spec:
- All primary connections exist with correct weights
- All secondary connections exist with correct weights
- Absent connections are correctly absent
"""

from agenetic.network.topology import (
    ALL_CONNECTIONS,
    PRIMARY_CONNECTIONS,
    SECONDARY_CONNECTIONS,
    SYSTEM_NAMES,
    ConnectionType,
    connection_exists,
    get_connections,
    get_weight,
)


class TestPrimaryConnections:
    """Verify all primary connections from the architecture spec."""

    def test_sensory_to_immune(self):
        assert connection_exists("sensory", "immune")
        assert get_weight("sensory", "immune") == 1.0

    def test_sensory_to_subconscious(self):
        assert connection_exists("sensory", "subconscious")
        assert get_weight("sensory", "subconscious") == 1.0

    def test_immune_to_conscious(self):
        assert connection_exists("immune", "conscious")
        assert get_weight("immune", "conscious") == 1.0

    def test_immune_to_motor(self):
        assert connection_exists("immune", "motor")
        assert get_weight("immune", "motor") == 1.0

    def test_subconscious_to_conscious(self):
        assert connection_exists("subconscious", "conscious")
        assert get_weight("subconscious", "conscious") == 1.0

    def test_subconscious_to_motor(self):
        assert connection_exists("subconscious", "motor")
        assert get_weight("subconscious", "motor") == 1.0

    def test_conscious_to_motor(self):
        assert connection_exists("conscious", "motor")
        assert get_weight("conscious", "motor") == 1.0

    def test_sleep_to_all_systems(self):
        for target in SYSTEM_NAMES:
            if target == "sleep":
                continue
            assert connection_exists("sleep", target), f"sleep -> {target} should exist"
            assert get_weight("sleep", target) == 1.0

    def test_genetic_to_all_except_motor(self):
        # Genetic reads to all systems except motor (absent by design).
        for target in ["sensory", "immune", "subconscious", "conscious", "sleep"]:
            assert connection_exists("genetic", target), f"genetic -> {target} should exist"
            assert get_weight("genetic", target) == 1.0

    def test_all_primary_are_weight_1(self):
        for conn in PRIMARY_CONNECTIONS:
            assert conn.weight == 1.0
            assert conn.connection_type == ConnectionType.PRIMARY


class TestSecondaryConnections:
    """Verify all secondary connections from the architecture spec."""

    def test_conscious_to_immune(self):
        assert connection_exists("conscious", "immune")
        assert get_weight("conscious", "immune") == 0.5

    def test_conscious_to_sensory(self):
        assert connection_exists("conscious", "sensory")
        assert get_weight("conscious", "sensory") == 0.5

    def test_conscious_to_subconscious(self):
        assert connection_exists("conscious", "subconscious")
        assert get_weight("conscious", "subconscious") == 0.5

    def test_motor_to_conscious(self):
        assert connection_exists("motor", "conscious")
        assert get_weight("motor", "conscious") == 0.5

    def test_immune_to_subconscious(self):
        assert connection_exists("immune", "subconscious")
        assert get_weight("immune", "subconscious") == 0.5

    def test_subconscious_to_immune(self):
        assert connection_exists("subconscious", "immune")
        assert get_weight("subconscious", "immune") == 0.5

    def test_all_secondary_are_weight_05(self):
        for conn in SECONDARY_CONNECTIONS:
            assert conn.weight == 0.5
            assert conn.connection_type == ConnectionType.SECONDARY


class TestAbsentConnections:
    """Verify connections that should NOT exist per the architecture spec."""

    def test_no_non_sleep_write_to_genetic(self):
        # Only sleep -> genetic should exist. No other system writes to genetic.
        for source in SYSTEM_NAMES:
            if source == "sleep":
                continue
            assert not connection_exists(source, "genetic"), (
                f"{source} -> genetic should not exist"
            )

    def test_no_motor_to_sensory(self):
        assert not connection_exists("motor", "sensory")

    def test_no_genetic_to_motor(self):
        assert not connection_exists("genetic", "motor")

    def test_absent_return_zero_weight(self):
        assert get_weight("motor", "sensory") == 0.0
        assert get_weight("genetic", "motor") == 0.0
        assert get_weight("sensory", "genetic") == 0.0


class TestTopologyHelpers:
    """Verify topology helper functions."""

    def test_system_names_has_seven(self):
        assert len(SYSTEM_NAMES) == 7

    def test_get_connections_by_source(self):
        conns = get_connections(source="sensory")
        assert all(c.source == "sensory" for c in conns)
        assert len(conns) == 2  # sensory -> immune, sensory -> subconscious

    def test_get_connections_by_target(self):
        conns = get_connections(target="motor")
        assert all(c.target == "motor" for c in conns)
        # immune->motor, subconscious->motor, conscious->motor, sleep->motor
        assert len(conns) == 4
