"""The seven information-processing systems of the Agenetic Framework."""

from agenetic.systems.base import BaseSystem, SystemState
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.genetic import GeneticSystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.subconscious import SubconsciousSystem

__all__ = [
    "BaseSystem",
    "SystemState",
    "SensorySystem",
    "ImmuneSystem",
    "SubconsciousSystem",
    "ConsciousSystem",
    "MotorSystem",
    "SleepSystem",
    "GeneticSystem",
]
