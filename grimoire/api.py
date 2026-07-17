import asyncio
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any

from weasyprint import HTML  # type: ignore

from python.methods import description_to_html, english_to_latin, markdown_to_html
from python.spell import SPELLS, Spell, SpellClass, get_spell

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")


@dataclass(frozen=True)
class FilterOptions:
    classes: list[SpellClass]
    schools: list[str]


class API:
    _debug: bool
    selected: set[Spell] = set()
    filter_options: FilterOptions

    def __init__(self, debug: bool):
        self._debug = debug
        self.filter_options = FilterOptions(classes=list(SPELLS.get_classes()), schools=SPELLS.get_schools())

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
        return [s.json for s in self.selected]

    def deselect(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = get_spell(name, source)
        if spell:
            logging.debug("Deselected - %s %s", name, source)
            self.selected.remove(spell)
        return [s.json for s in self.selected]

    def export_pdf(self, name: str, source: str):
        spell = get_spell(name, source)
        if spell is None:
            logging.warning("Could not find Spell - %s %s", name, source)
            return f"{name} {source} - Could not find Spell"

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            template_content = file.read()

        description = description_to_html(spell.description)
        vocal_component = ""
        if "V" in spell.components:
            vocal_component = asyncio.run(english_to_latin(spell.name))
            if spell.level == "Cantrip":
                vocal_component = vocal_component.split(" ")[0]

        filled_html = template_content.format(
            name=spell.name,
            source=spell.source,
            subtitle=spell.subtitle,
            vocal=vocal_component,
            casting=spell.casting_time,
            range=spell.spell_range,
            components=spell.components,
            duration=markdown_to_html(spell.duration),
            description=markdown_to_html(description),
        )

        formatted_name = spell.name.lower().replace(" ", "_")
        filename = f"{spell.source}_{formatted_name}.pdf"
        output_path = f"generated/{filename}"
        os.makedirs("generated", exist_ok=True)
        base_path = os.path.dirname(TEMPLATE_PATH)

        if self._debug:
            debug_path = os.path.join(os.path.dirname(__file__), "_debug.html")
            with open(debug_path, "w", encoding="utf-8") as debug_file:
                debug_file.write(filled_html)

        try:
            HTML(string=filled_html, base_url=base_path).write_pdf(output_path)  # type: ignore
        except TypeError as e:
            logging.error("Error generating %s %s - %s", formatted_name, source, e)
            return f"{formatted_name} {source} - Error generating PDF layout."

        logging.debug("Generated %s", filename)
        return f"Created {filename} successfully!"

    def export_selected_to_pdf(self) -> str:
        # TODO Generate 1 full PDF, rather than x separate ones.
        summary: list[str] = []
        for spell in self.selected:
            result = self.export_pdf(spell.name, spell.source)
            summary.append(result)
        return "\n".join(summary)
