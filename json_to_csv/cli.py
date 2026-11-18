#!/usr/bin/env python3
"""Command-line entry point for json-to-csv.

Usage:
    json-to-csv data.json
    json-to-csv data.json -o out.csv
    cat data.json | json-to-csv --fields name,age --delimiter ';'
"""

import argparse
import json
import sys

from json_to_csv import convert_json_text


def build_parser():
    parser = argparse.ArgumentParser(
        prog="json-to-csv",
        description="Convert a JSON array of objects (or a single object) to CSV.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="input JSON file (default: read from stdin)",
    )
    parser.add_argument("-o", "--output", help="output CSV file (default: stdout)")
    parser.add_argument(
        "--fields",
        help="comma-separated column list, in output order (default: all keys, first-seen order)",
    )
    parser.add_argument(
        "--no-flatten",
        action="store_true",
        help="do not flatten nested objects; write them as JSON strings instead",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter (default: ',')",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as fh:
                text = fh.read()
        else:
            text = sys.stdin.read()
    except OSError as exc:
        print("json-to-csv: cannot read input: %s" % exc, file=sys.stderr)
        return 1
    fields = (
        [f.strip() for f in args.fields.split(",") if f.strip()]
        if args.fields
        else None
    )
    try:
        out = convert_json_text(
            text,
            fields=fields,
            flatten_nested=not args.no_flatten,
            delimiter=args.delimiter,
        )
    except json.JSONDecodeError as exc:
        print("json-to-csv: invalid JSON: %s" % exc, file=sys.stderr)
        return 1
    except ValueError as exc:
        print("json-to-csv: %s" % exc, file=sys.stderr)
        return 1
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="") as fh:
                fh.write(out)
        except OSError as exc:
            print("json-to-csv: cannot write output: %s" % exc, file=sys.stderr)
            return 1
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
