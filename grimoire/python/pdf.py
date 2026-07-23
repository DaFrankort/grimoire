import logging
import os
import time

from weasyprint import HTML, Document  # type: ignore

from python.spell import Spell, get_spell

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "template.html")


def render_spell_doc(html_content: str, base_path: str, min_font_size: float = 10.0) -> Document:
    """
    Iteratively scales down font-size until HTML fits on 1 page.
    Returns a compiled WeasyPrint Document.
    """
    current_font_size = 16.0
    step = 0.5

    while current_font_size > min_font_size:
        scaled_style = f"<style>body {{ font-size: {current_font_size}px !important; }}</style>"
        doc = HTML(string=f"{scaled_style}\n{html_content}", base_url=base_path).render()  # type: ignore

        if len(doc.pages) <= 1:  # type: ignore
            return doc
        logging.warning("Spell exceeds one page, shrinking font size: %s => %s", current_font_size, current_font_size - step)
        current_font_size -= step

    scaled_style = f"<style>body {{ font-size: {min_font_size}px !important; }}</style>"
    return HTML(string=f"{scaled_style}\n{html_content}", base_url=base_path).render()  # type: ignore


def export_pdf(name: str, source: str) -> str:
    spell = get_spell(name, source)
    if spell is None:
        logging.warning("Could not find Spell - %s %s", name, source)
        return f"{name} {source} - Could not find Spell"

    filled_html = spell.render_html(TEMPLATE_PATH)
    filename = spell.get_filename()
    output_path = f"generated/{filename}"
    os.makedirs("generated", exist_ok=True)
    base_path = os.path.dirname(TEMPLATE_PATH)

    doc = render_spell_doc(filled_html, base_path)
    doc.write_pdf(output_path)  # type: ignore

    logging.debug("Generated %s", filename)
    return filename


def export_selected_to_pdf(selected: set[Spell]) -> str:
    if not selected:
        return "No spells selected."

    sorted_selected = sorted(selected, key=lambda spell: (spell.level_int, spell.name.lower()))
    base_path = os.path.dirname(TEMPLATE_PATH)

    docs: list[Document] = []
    for spell_item in sorted_selected:
        spell = get_spell(spell_item.name, spell_item.source)
        if spell is None:
            logging.warning("Could not find Spell - %s %s", spell_item.name, spell_item.source)
            continue

        html = spell.render_html(TEMPLATE_PATH)
        docs.append(render_spell_doc(html, base_path))

    if not docs:
        return "No valid spells found to render."

    master_doc = docs[0]
    for doc in docs[1:]:
        master_doc.pages.extend(doc.pages)  # type: ignore

    os.makedirs("generated", exist_ok=True)
    timestamp = int(time.time())
    filename = f"{len(selected)}_spells_{timestamp}.pdf"
    output_path = f"generated/{filename}"

    master_doc.write_pdf(output_path)  # type: ignore
    logging.debug("Generated bundle %s", filename)
    return f"Created combined PDF with {len(docs)} spells at {filename}."
