import os
import webview


class ToolAPI:
    def greet_user(self, name: str):
        return f"Hello, {name}! This response came straight from Python."


if __name__ == "__main__":
    api = ToolAPI()
    html_path = os.path.join(os.path.dirname(__file__), "frontend/index.html")

    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600)  # type: ignore
    webview.start()
