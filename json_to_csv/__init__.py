"""json-to-csv — convert JSON (array of objects) to CSV."""

from .converter import convert_json_text, flatten, to_csv_text

__version__ = "1.0.0"
__all__ = ["convert_json_text", "flatten", "to_csv_text"]
