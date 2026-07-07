import os
from typing import Any

from xhtml2pdf import pisa  # type: ignore

from python.methods import description_to_html, markdown_to_html
from python.spell import SPELLS, Spell, get_spell

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")


class API:  # type: ignore
    selected: set[Spell] = set()

    def fetch(self) -> list[dict[str, str | int | None]]:
        return sorted(
            (s.json for s in SPELLS.entries if s not in self.selected),
            key=lambda spell: (spell["level"], spell["name"]),
        )

    def select(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = get_spell(name, source)
        if spell:
            self.selected.add(spell)
        return [s.json for s in self.selected]

    def deselect(self, name: str, source: str) -> list[dict[str, Any]]:
        spell = get_spell(name, source)
        if spell:
            self.selected.remove(spell)
        return [s.json for s in self.selected]

    def export_pdf(self, name: str, source: str):
        spell = get_spell(name, source)
        if spell is None:
            return f"{name} {source} - Could not find Spell"

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            template_content = file.read()

        description = description_to_html(spell.description)
        filled_html = template_content.format(
            name=spell.name,
            source=spell.source,
            subtitle=spell.subtitle,
            casting=spell.casting_time,
            range=spell.spell_range,
            components=spell.components,
            duration=markdown_to_html(spell.duration),
            description=markdown_to_html(description),
        )

        name = spell.name.lower().replace(" ", "_")
        filename = f"{spell.source}_{name}.pdf"
        output_path = f"generated/{filename}"
        os.makedirs("generated", exist_ok=True)

        base_path = os.path.dirname(TEMPLATE_PATH)
        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(filled_html, dest=pdf_file, path=base_path)  # type: ignore

        if pisa_status.err:  # type: ignore
            return f"{name} {source} - Error generating PDF layout."

        print(f"- Generated {filename}")
        return f"Created {filename} successfully!"

    def export_selected_to_pdf(self) -> str:
        # TODO Generate 1 full PDF, rather than x separate ones.
        summary: list[str] = []
        for spell in self.selected:
            result = self.export_pdf(spell.name, spell.source)
            summary.append(result)
        return "\n".join(summary)
