import re

from googletrans import Translator  # type: ignore

from python.dnd_abstract import (
    Description,
    DescriptionList,
    DescriptionListList,
    DescriptionTable,
    DescriptionTableTable,
    DescriptionText,
)


def markdown_to_html(text: str) -> str:
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"__(.*?)__", r"<u>\1</u>", text)
    return text


def _text_to_html(desc: DescriptionText) -> str:
    prefix = f"<strong>{desc['name']}.</strong> " if desc.get("name") else ""
    return f"<p>{prefix}{desc['value']}</p>"


def _table_to_html(desc: DescriptionTable) -> str:
    table_data: DescriptionTableTable = desc["table"]
    table_html: list[str] = []

    if table_data.get("title"):
        table_html.append(f"<caption>{table_data['title']}</caption>")

    table_html.append("<table>")

    if table_data["headers"]:
        table_html.append("<thead><tr>")
        for header in table_data["headers"]:
            table_html.append(f"<th>{header}</th>")
        table_html.append("</tr></thead>")

    table_html.append("<tbody>")
    for row in table_data["rows"]:
        table_html.append("<tr>")
        for cell in row:
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

    return "".join(table_html)


def _render_list_helper(desc_list: DescriptionListList) -> str:
    inner_html = ["<ul>"]
    for entry in desc_list["entries"]:
        if isinstance(entry, dict) and entry.get("type") == "list":
            inner_html.append(f"<li>{_render_list_helper(entry)}</li>")
        else:
            inner_html.append(f"<li>{entry}</li>")
    inner_html.append("</ul>")
    return "".join(inner_html)


def _list_to_html(desc: DescriptionList) -> str:
    list_data = desc["list"]
    list_html: list[str] = []

    if list_data.get("caption"):
        list_html.append(f"<p><strong>{list_data['caption']}</strong></p>")

    list_html.append(_render_list_helper(list_data))
    return "".join(list_html)


def description_to_html(description: list[Description]) -> str:
    html_chunks: list[str] = []

    for desc in description:
        if desc["type"] == "text":
            html_chunks.append(_text_to_html(desc))
        elif desc["type"] == "table":
            html_chunks.append(_table_to_html(desc))
        elif desc["type"] == "list":
            html_chunks.append(_list_to_html(desc))

    html = "".join(html_chunks)
    return html


async def english_to_latin(text: str) -> str:
    async with Translator() as translator:
        result = await translator.translate(text, src="en", dest="la")
        return result.text
