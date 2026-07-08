import argparse
import logging
import os

import webview


class PrettyFormatter(logging.Formatter):
    # ANSI Escape sequences for clean terminal colors
    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # Comprehensive layout: [Timestamp] [Level] (Filename:Line) Message
    # Fixed-width alignments keep logs beautifully structured in columns
    FORMAT = "[%(asctime)s] %(levelname)-8s| (%(filename)s:%(lineno)d) %(message)s"

    FORMATS = {
        logging.DEBUG: cyan + FORMAT + reset,
        logging.INFO: grey + FORMAT + reset,
        logging.WARNING: yellow + FORMAT + reset,
        logging.ERROR: red + FORMAT + reset,
        logging.CRITICAL: bold_red + FORMAT + reset,
    }

    def format(self, record):  # type: ignore
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


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
    handler.setFormatter(PrettyFormatter())
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    from api import (
        API,  # Load api later, to initialize python code with the configured logger.
    )

    api = API()

    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    webview.create_window(title="Grimoire", url=html_path, js_api=api, width=800, height=600, maximized=True)  # type: ignore
    webview.start(debug=args.debug)
    logging.info("Grimoire started.")
