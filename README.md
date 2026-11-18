# json-to-csv

Convert a JSON array of objects (or a single object) to CSV — from a file or
stdin. Zero dependencies, Python 3.9+.

## Install

```bash
pip install .
```

## Usage

```bash
# From a file
json-to-csv data.json

# From stdin
cat data.json | json-to-csv

# Pick (and order) the columns
json-to-csv data.json --fields name,age,city

# Use a different delimiter
json-to-csv data.json --delimiter ';'

# Write to a file
json-to-csv data.json -o out.csv
```

## Behaviour

- The header row is the union of all object keys, in order of first
  appearance. Missing keys become empty cells.
- Nested objects are flattened to dotted keys by default
  (`{"address": {"city": "Swabi"}}` → column `address.city`).
  Pass `--no-flatten` to write nested values as JSON strings instead.
- `null` becomes an empty cell; booleans become `true` / `false`.
- A single JSON object is treated as one row; an empty array produces no
  output. Rows that are not objects are rejected with a clear error.

## Example

Input:

```json
[
  {"name": "Ali", "age": 22, "address": {"city": "Swabi"}},
  {"name": "Sara", "age": 25}
]
```

Output:

```csv
name,age,address.city
Ali,22,Swabi
Sara,25,
```

## Tests

```bash
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
