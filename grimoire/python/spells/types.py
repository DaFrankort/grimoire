from dataclasses import dataclass
from typing import Literal

SpellSchool = Literal["A", "C", "D", "E", "I", "N", "V", "T"]


@dataclass
class SpellComponent:
    vocal: bool = False
    somantic: bool = False
    ritual: bool = False
    material: str | None = None
