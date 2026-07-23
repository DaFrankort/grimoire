import logging
from dataclasses import asdict, dataclass
from typing import Any

from python.pdf import export_pdf, export_selected_to_pdf
from python.spell import SPELLS, Spell, SpellClass, get_spell


@dataclass(frozen=True)
class FilterOptions:
    classes: list[SpellClass]
    schools: list[str]
    levels: list[str]


class API:
    _debug: bool
    selected: set[Spell] = set()
    filter_options: FilterOptions

    def __init__(self, debug: bool):
        self._debug = debug
        self.filter_options = FilterOptions(
            classes=list(SPELLS.get_classes()), schools=SPELLS.get_schools(), levels=SPELLS.get_levels()
        )

    @property
    def _selected_json(self) -> list[dict[str, Any]]:
        return [s.json for s in self.selected]

    def get_filter_options(self) -> dict[str, Any]:
        return asdict(self.filter_options)

    def fetch(self) -> list[dict[str, str | int | None]]:
        spells = sorted(
            (s.json for s in SPELLS.entries if s not in self.selected),
            key=lambda spell: (spell["level"], spell["name"]),
        )
        logging.debug("Loaded %s spells.", len(spells))
        return spells

    def select(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = get_spell(name, source)
        if spell:
            logging.debug("Selected - %s %s", name, source)
            self.selected.add(spell)
        return self._selected_json

    def deselect(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = get_spell(name, source)
        if spell:
            logging.debug("Deselected - %s %s", name, source)
            self.selected.remove(spell)
        return self._selected_json

    def export_pdf(self, name: str, source: str) -> str:
        return export_pdf(name, source)

    def export_selected_to_pdf(self) -> str:
        return export_selected_to_pdf(self.selected)
