"""Command line entry point.

Reads a JSON summary file and prints the health report. The file holds
one table object or a list of table objects in the shape described in
docs/summary-format.md.
"""

import argparse
import json
import sys

from .report import render_json, render_markdown, render_report
from .scoring import summary_from_dict

RENDERERS = {"text": render_report, "json": render_json, "markdown": render_markdown}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a read only Iceberg table health check.")
    parser.add_argument("command", choices=["check"], help="The command to run")
    parser.add_argument("--summary", required=True, help="Path to a JSON table summary file")
    parser.add_argument(
        "--format",
        choices=sorted(RENDERERS),
        default="text",
        help="How to print the report, text by default",
    )
    args = parser.parse_args(argv)

    with open(args.summary) as handle:
        data = json.load(handle)
    tables = data if isinstance(data, list) else [data]
    summaries = [summary_from_dict(item) for item in tables]
    print(RENDERERS[args.format](summaries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
