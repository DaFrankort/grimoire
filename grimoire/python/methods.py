import re
from typing import Literal, Sequence, TypedDict

from googletrans import Translator  # type: ignore


class DescriptionRowRange(TypedDict):
    type: Literal["range"]
    min: int
    max: int


class DescriptionText(TypedDict):
    name: str
    type: Literal["text"]
    value: str


class DescriptionTableTable(TypedDict):
    type: Literal["table"]
    title: str
    headers: list[str] | None
    rows: Sequence[Sequence[str | DescriptionRowRange | int | None]]


class DescriptionTable(TypedDict):
    name: str
    type: Literal["table"]
    table: DescriptionTableTable


class DescriptionListList(TypedDict):
    type: Literal["list"]
    caption: str
    entries: list["str | DescriptionListList"]


class DescriptionList(TypedDict):
    name: str
    type: Literal["list"]
    list: DescriptionListList


Description = DescriptionTable | DescriptionText | DescriptionList


def markdown_to_html(text: str) -> str:
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"__(.*?)__", r"<u>\1</u>", text)
    return text


def description_to_html(description: list[Description]) -> str:
    html_chunks: list[str] = []

    for desc in description:
        if desc["type"] == "text":
            prefix = f"<strong>{desc['name']}.</strong> " if desc.get("name") else ""
            html_chunks.append(f"<p>{prefix}{desc['value']}</p>")

        elif desc["type"] == "table":
            table_data = desc["table"]
            table_html: list[str] = []

            if table_data.get("title"):
                table_html.append(f"<caption>{table_data['title']}</caption>")

            table_html.append("<table>")

            if table_data.get("headers"):
                table_html.append("<thead><tr>")
                for header in table_data["headers"]:  # type: ignore
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

            html_chunks.append("".join(table_html))

        elif desc["type"] == "list":
            list_data = desc["list"]
            list_html: list[str] = []

            if list_data.get("caption"):
                list_html.append(f"<p><strong>{list_data['caption']}</strong></p>")

            def render_list(lst_obj) -> str:  # type: ignore
                inner_html = ["<ul>"]
                for entry in lst_obj["entries"]:  # type: ignore
                    if isinstance(entry, dict) and entry.get("type") == "list":  # type: ignore
                        inner_html.append(f"<li>{render_list(entry)}</li>")
                    else:
                        inner_html.append(f"<li>{entry}</li>")
                inner_html.append("</ul>")
                return "".join(inner_html)

            list_html.append(render_list(list_data))
            html_chunks.append("".join(list_html))

    html = "".join(html_chunks)
    return html


async def english_to_latin(text: str) -> str:
    async with Translator() as translator:
        result = await translator.translate(text, src="en", dest="la")
        return result.text
