import os
import webview

from logic.spell import SPELLS


class ToolAPI:

    def greet_user(self, name: str) -> str:
        return f"Hello, {name}! This response came straight from Python."

    def fetch_spells(self) -> list[dict[str, str | int | None]]:
        return [
            {
                "name": s.name,
                "source": s.source,
                "level": s.level.replace("Level", "").strip(),
                "school": s.school,
                "url": s.url,
            }
            for s in SPELLS.entries
        ]


if __name__ == "__main__":
    api = ToolAPI()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600)  # type: ignore
    webview.start()
