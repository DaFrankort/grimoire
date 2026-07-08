import asyncio
import logging
import os
from dataclasses import asdict
from typing import Any

from weasyprint import HTML  # type: ignore

from python.methods import english_to_latin, markdown_to_html
from python.spells import Spell, SpellList

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")


class API:
    selected: set[Spell]
    spells: SpellList

    def __init__(self):
        self.selected = set()
        self.spells = SpellList()
        pass

    def fetch(self) -> list[dict[str, str | int | None]]:
        spells = [asdict(s) for s in self.spells.get_all()]
        logging.debug(f"Loaded {len(spells)} spells.")
        return spells

    def select(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = self.spells.get(name, source)
        if spell:
            logging.debug(f"Selected - {name} {source}")
            self.selected.add(spell)
        return [asdict(s) for s in self.selected]

    def deselect(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = self.spells.get(name, source)
        if spell:
            logging.debug(f"Deselected - {name} {source}")
            self.selected.remove(spell)
        return [asdict(s) for s in self.selected]

    def export_pdf(self, name: str, source: str):
        spell = self.spells.get(name, source)
        if spell is None:
            logging.warning(f"Could not find Spell - {name} ({source})")
            return f"{name} {source} - Could not find Spell"

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            template_content = file.read()

        description = "placeholder"  # TODO spell.entries
        vocal_component = ""
        if spell.components.vocal:
            vocal_component = asyncio.run(english_to_latin(spell.name))
            if spell.level == 0:
                vocal_component = vocal_component.split(" ")[0]
        subtitle = f"{spell.level_str} {spell.school}"

        filled_html = template_content.format(
            name=spell.name,
            source=spell.source,
            subtitle=subtitle,
            vocal=vocal_component,
            casting="spell.casting_time",  # TODO
            range="spell.spell_range",  # TODO
            components=spell.components,
            duration="markdown_to_html(spell.duration)",  # TODO
            description=markdown_to_html(description),
        )

        formatted_name = spell.name.lower().replace(" ", "_")
        filename = f"{spell.source}_{formatted_name}.pdf"
        output_path = f"generated/{filename}"
        os.makedirs("generated", exist_ok=True)
        base_path = os.path.dirname(TEMPLATE_PATH)

        if True:  # Debugging
            debug_path = os.path.join(os.path.dirname(__file__), "_debug.html")
            with open(debug_path, "w", encoding="utf-8") as debug_file:
                debug_file.write(filled_html)

        try:
            HTML(string=filled_html, base_url=base_path).write_pdf(output_path)  # type: ignore
        except Exception as e:
            logging.error(f"Error generating {formatted_name} {source} - {e}")
            return f"{formatted_name} {source} - Error generating PDF layout."

        logging.debug(f"Generated {filename}")
        return f"Created {filename} successfully!"

    def export_selected_to_pdf(self) -> str:
        # TODO Generate 1 full PDF, rather than x separate ones.
        summary: list[str] = []
        for spell in self.selected:
            result = self.export_pdf(spell.name, spell.source)
            summary.append(result)
        return "\n".join(summary)
