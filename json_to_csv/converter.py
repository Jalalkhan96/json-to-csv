"""Convert JSON data (an array of objects, or a single object) to CSV text.

Values are written with the csv module (minimal quoting). Nested dicts are
flattened to dotted keys (``{"a": {"b": 1}}`` -> column ``a.b``) unless
flattening is turned off, in which case nested values are written as JSON
strings. ``None`` becomes an empty cell; booleans become ``true``/``false``.
"""

import csv
import io
import json

__all__ = ["flatten", "collect_fields", "to_csv_text", "convert_json_text"]


def flatten(obj, parent_key="", sep="."):
    """Flatten a nested dict to a single level with dotted keys.

    Lists and other non-dict values are left as-is (the caller stringifies
    them); empty dicts become an empty string under their own key.
    """
    items = {}
    if not isinstance(obj, dict):
        return items
    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)
        if isinstance(value, dict):
            if value:
                items.update(flatten(value, new_key, sep=sep))
            else:
                items[new_key] = ""
        else:
            items[new_key] = value
    return items


def _stringify(value):
    """Render one cell value as a string for the CSV output."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def collect_fields(rows, fields=None):
    """Return the column list: the given fields, or the union of all row
    keys in order of first appearance."""
    if fields is not None:
        return list(fields)
    seen = []
    for row in rows:
        for key in row:
            if key not in seen:
                seen.append(key)
    return seen


def to_csv_text(data, fields=None, flatten_nested=True, delimiter=","):
    """Convert parsed JSON data to CSV text (with a header row).

    ``data`` is a list of dicts, or a single dict (one row). An empty list
    produces an empty string. Rows that are not dicts raise ValueError.
    """
    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("JSON input must be an object or an array of objects")
    if not rows:
        return ""
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("every row must be a JSON object, got: %r" % (row,))
    if flatten_nested:
        rows = [flatten(row) for row in rows]
    columns = collect_fields(rows, fields)
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_stringify(row.get(col)) for col in columns])
    return buf.getvalue()


def convert_json_text(text, fields=None, flatten_nested=True, delimiter=","):
    """Parse a JSON string and convert it to CSV text."""
    return to_csv_text(
        json.loads(text),
        fields=fields,
        flatten_nested=flatten_nested,
        delimiter=delimiter,
    )
