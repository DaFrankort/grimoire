from dataclasses import dataclass
from typing import Any

from python.dnd_abstract import Description, DNDEntry, DNDEntryList


@dataclass(frozen=True)
class SpellClass:
    name: str
    source: str

    def __str__(self) -> str:
        return f"{self.name} ({self.source})"


class Spell(DNDEntry):
    """A class representing a Dungeons & Dragons spell."""

    level: str
    school: str
    casting_time: str
    spell_range: str
    components: str
    duration: str
    description: list[Description]
    classes: list[SpellClass]

    def __init__(self, obj: dict[str, Any]):
        super().__init__(obj)
        self.entry_type = "spell"

        self.name = obj["name"]
        self.source = obj["source"]
        self.url = obj["url"]

        self.level = obj["level"]
        self.school = obj["school"]
        self.casting_time = obj["castingTime"]
        self.spell_range = obj["range"]
        self.components = obj["components"]
        self.duration = obj["duration"]
        self.description = obj["description"]
        self.classes = [SpellClass(c["name"], c["source"]) for c in obj.get("classes", [])]

        self.select_description = f"{self.level} {self.school}"

    def __str__(self):
        return f"{self.name} ({self.source})"

    def __repr__(self):
        return str(self)

    def get_formatted_classes(self, allowed_sources: set[str]):
        classes: set[str] = set()
        for class_ in self.classes:
            if class_.source not in allowed_sources:
                continue
            classes.add(class_.name)
        return ", ".join(sorted(list(classes)))

    @property
    def level_school(self) -> str:
        return f"{self.level} {self.school}"

    @property
    def level_int(self) -> int:
        """Returns the level as an integer."""
        if self.level == "Cantrip":
            return 0
        return int(self.level.replace("Level", "").strip())

    @property
    def subtitle(self) -> str:
        return f"{self.level} {self.school}"


class SpellList(DNDEntryList[Spell]):
    type = Spell
    paths = ["spells.json"]

    def get_classes(self) -> set[SpellClass]:
        """Returns all classes used by spells."""
        classes: set[SpellClass] = set()
        for spell in self.entries:
            for c in spell.classes:
                classes.add(c)
        return classes

    def get_schools(self) -> list[str]:
        """Returns all schools used by spells in alphabetical order."""
        schools: set[str] = set()
        for spell in self.entries:
            schools.add(spell.school.lower())
        return sorted(list(schools))


def get_spell(name: str, source: str) -> Spell | None:
    spell = [s for s in SPELLS.get(name, allowed_sources={source}) if s.source == source]
    if len(spell) == 0:
        return None
    return spell[0]


SPELLS = SpellList()
