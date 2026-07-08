from dataclasses import dataclass, field
from typing import Any, Literal, Optional


@dataclass
class EntryInset:
    type: Literal["inset"] = field(init=False, default="inset")
    name: str
    entries: list["Entry"]
    source: str | None
    page: int | None

    def __str__(self) -> str:
        text = "".join(str(e) for e in self.entries)

        footer = ""
        if self.source:
            footer = f'<div class="inset-source">{self.source}'
            if self.page is not None:
                footer += f", p. {self.page}"
            footer += "</div>"

        return '<div class="inset">' f"<strong>{self.name}</strong>" f"<div>{text}</div>" f"{footer}" "</div>"


@dataclass
class EntryQuote:
    type: Literal["quote"] = field(init=False, default="quote")
    entries: list["Entry"]
    by: str

    def __str__(self) -> str:
        text = "<br>".join(str(entry) for entry in self.entries)
        return f"<blockquote>{text}" f"<footer>&mdash; {self.by}</footer>" f"</blockquote>"


@dataclass
class EntryItem:
    type: Literal["item"] = field(init=False, default="item")
    name: str
    entries: list["Entry"]

    def __str__(self) -> str:
        # TODO Check actual styling
        text = "".join(str(e) for e in self.entries)
        return f"<strong>{self.name}</strong> - {text}"


@dataclass
class EntryList:
    type: Literal["list"] = field(init=False, default="list")
    style: Optional[str]  # TODO Unused
    items: list["Entry"]

    def __str__(self) -> str:
        list_items = "".join([f"<li>{item}</li>" for item in self.items])
        return f"<ul>{list_items}</ul>"


@dataclass
class EntryEntries:
    type: Literal["entries"] = field(init=False, default="entries")
    name: str
    entries: list["Entry"]

    def __str__(self) -> str:
        text = "".join(str(e) for e in self.entries)
        return f"<strong>{self.name}:</strong> {text}"


@dataclass
class EntryTable:
    type: Literal["table"] = field(init=False, default="table")
    caption: str
    colStyles: list[str]  # TODO Apply these somehow?
    colLabels: list[str]
    rows: list[list[str]]

    def __str__(self) -> str:
        html = ["<table>"]

        if self.caption:
            html.append(f"<caption>{self.caption}</caption>")

        if self.colLabels:
            html.append("<thead>")
            html.append("<tr>")
            for label in self.colLabels:
                html.append(f"<th>{label}</th>")
            html.append("</tr>")
            html.append("</thead>")

        if self.rows:
            html.append("<tbody>")
            for row in self.rows:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</tbody>")
        html.append("</table>")
        return "\n".join(html)


Entry = str | EntryTable | EntryEntries | EntryList | EntryItem | EntryQuote | EntryInset


def parse_entries(entries: list[Any]) -> list[Entry]:
    parsed: list[Entry] = []

    for entry in entries:
        if isinstance(entry, str):
            parsed.append(entry)
            continue

        if not isinstance(entry, dict):
            raise TypeError(f"Unsupported entry type: {entry}")

        entry_type = entry.get("type", None)  # type: ignore
        if entry_type is None:
            raise KeyError(f"Entry does not have type-key: {entry}")

        match entry_type:
            case "list":
                parsed.append(
                    EntryList(
                        style=entry.get("style"),  # type: ignore
                        items=parse_entries(entry.get("items", [])),  # type: ignore
                    )
                )

            case "entries":
                parsed.append(
                    EntryEntries(
                        name=entry["name"],  # type: ignore
                        entries=parse_entries(entry.get("entries", [])),  # type: ignore
                    )
                )

            case "quote":
                parsed.append(
                    EntryQuote(
                        entries=parse_entries(entry.get("entries", [])),  # type: ignore
                        by=entry.get("by", ""),  # type: ignore
                    )
                )

            case "inset":
                parsed.append(
                    EntryInset(
                        name=entry["name"],  # type: ignore
                        entries=parse_entries(entry.get("entries", [])),  # type: ignore
                        source=entry.get("source"),  # type: ignore
                        page=entry.get("page"),  # type: ignore
                    )
                )

            case "table":
                parsed.append(
                    EntryTable(
                        caption=entry.get("caption", ""),  # type: ignore
                        colStyles=entry.get("colStyles", []),  # type: ignore
                        colLabels=entry.get("colLabels", []),  # type: ignore
                        rows=entry.get("rows", []),  # type: ignore
                    )
                )

            case "item":
                parsed.append(
                    EntryItem(
                        name=entry["name"],  # type: ignore
                        entries=parse_entries(entry.get("entries", [])),  # type: ignore
                    )
                )

            case _:  # type: ignore
                raise ValueError(f"Unknown entry type: {entry}")

    return parsed
