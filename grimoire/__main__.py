import os
import re

import webview
from xhtml2pdf import pisa  # type: ignore

from logic.dnd_abstract import Description
from logic.spell import SPELLS

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")


class ToolAPI:  # type: ignore

    def fetch_spells(self) -> list[dict[str, str | int | None]]:
        return [s.json for s in SPELLS.entries]

    def _markdown_to_html(self, text: str) -> str:
        text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
        text = re.sub(r"__(.*?)__", r"<u>\1</u>", text)
        return text

    def _description_to_html(self, description: list[Description]) -> str:
        html_chunks: list[str] = []

        for desc in description:
            # 1. Handle plain text entries
            if desc["type"] == "text":
                # bold the name if it's an inline subheading (common in D&D blocks)
                prefix = f"<strong>{desc['name']}.</strong> " if desc.get("name") else ""
                html_chunks.append(f"<p>{prefix}{desc['value']}</p>")

            # 2. Handle structured tables
            elif desc["type"] == "table":
                table_data = desc["table"]
                table_html: list[str] = []

                if table_data.get("title"):
                    table_html.append(f"<caption>{table_data['title']}</caption>")

                table_html.append("<table>")

                # Build Headers
                if table_data.get("headers"):
                    table_html.append("<thead><tr>")
                    for header in table_data["headers"]:  # type: ignore
                        table_html.append(f"<th>{header}</th>")
                    table_html.append("</tr></thead>")

                # Build Rows
                table_html.append("<tbody>")
                for row in table_data["rows"]:
                    table_html.append("tr")
                    for cell in row:
                        # Handle specific dict structures inside cell grids
                        if isinstance(cell, dict) and cell.get("type") == "range":
                            if cell["min"] == cell["max"]:
                                cell_val = str(cell["min"])
                            else:
                                cell_val = f"{cell['min']}-{cell['max']}"
                        else:
                            cell_val = str(cell) if cell is not None else ""

                        table_html.append(f"<td>{cell_val}</td>")
                    table_html.append("</tr>")
                table_html.append("</tbody></table>")

                html_chunks.append("".join(table_html))

            # 3. Handle list structures
            elif desc["type"] == "list":
                list_data = desc["list"]
                list_html: list[str] = []

                if list_data.get("caption"):
                    list_html.append(f"<p><strong>{list_data['caption']}</strong></p>")

                # Nested recursive helper function to handle lists inside lists
                def render_list(lst_obj) -> str:  # type: ignore
                    inner_html = ["<ul>"]
                    for entry in lst_obj["entries"]:  # type: ignore
                        if isinstance(entry, dict) and entry.get("type") == "list":  # type: ignore
                            # If it's a nested list dictionary, recurse
                            inner_html.append(f"<li>{render_list(entry)}</li>")
                        else:
                            inner_html.append(f"<li>{entry}</li>")
                    inner_html.append("</ul>")
                    return "".join(inner_html)

                list_html.append(render_list(list_data))
                html_chunks.append("".join(list_html))

        html = "".join(html_chunks)
        return self._markdown_to_html(html)

    def export_spell_pdf(self, name: str, source: str):
        spell = SPELLS.get(name, allowed_sources=set(source))
        if len(spell) == 0:
            return f"Could not find Spell {name} {source}"
        spell = spell[0]

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            template_content = file.read()

        filled_html = template_content.format(
            name=spell.name,
            level=spell.level_int,
            school=spell.school,
            source=spell.source,
            description=self._description_to_html(spell.description),
        )

        name = spell.name.lower().replace(" ", "_")
        filename = f"{spell.source}_{name}.pdf"
        output_path = f"generated/{filename}"

        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(filled_html, dest=pdf_file)  # type: ignore

        if pisa_status.err:  # type: ignore
            return "Error generating PDF layout."

        return f"Created {filename} successfully!"


if __name__ == "__main__":
    api = ToolAPI()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600)  # type: ignore
    webview.start()
