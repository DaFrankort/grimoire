import os

import webview

from python.api import API

if __name__ == "__main__":
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600, maximized=True)  # type: ignore
    webview.start()
