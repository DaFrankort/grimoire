from dataclasses import dataclass
from typing import Literal, Optional

SpellSchool = Literal["A", "C", "D", "E", "I", "N", "V", "T"]
AreaTags = Literal["MT", "ST"]
Ability = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
CreatureTypes = Literal["TODO"]  # TODO
Condition = Literal["TODO"]  # TODO
DamageType = Literal["TODO"]  # TODO


@dataclass
class SpellComponent:
    vocal: bool = False
    somantic: bool = False
    ritual: bool = False
    material: str | None = None


@dataclass
class SpellRange:
    class SpellRangeDistance:
        type: Literal["feet"]
        amount: int

    type: Literal["point"]  # TODO
    distance: SpellRangeDistance


@dataclass
class SpellTime:
    number: int
    unit: str

    def __str__(self) -> str:
        if self.number == 1:
            return f"{self.number} {self.unit}"
        return f"{self.number} {self.unit}s"


@dataclass
class SpellDuration:
    type: Literal["permanent", "instant"]
    ends: Optional[list[Literal["dispel"]]]
