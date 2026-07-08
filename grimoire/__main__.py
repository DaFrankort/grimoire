import argparse
import logging
import os

import webview

from api import API

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Enable debug mode with additional logging, Disabled by default.",
    )

    args = parser.parse_args()

    handler = logging.StreamHandler()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    api = API()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600, maximized=True)  # type: ignore
    webview.start(debug=args.debug)
    logging.info("Grimoire started.")
