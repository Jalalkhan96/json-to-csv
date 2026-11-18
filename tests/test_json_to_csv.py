"""Tests for json-to-csv."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from json_to_csv import convert_json_text, flatten, to_csv_text

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "json_to_csv" / "cli.py"


def test_basic_array_of_objects():
    out = to_csv_text([{"name": "Ali", "age": 22}, {"name": "Sara", "age": 25}])
    assert out == "name,age\nAli,22\nSara,25\n"


def test_missing_keys_become_empty_cells():
    out = to_csv_text([{"name": "Ali", "age": 22}, {"name": "Sara"}])
    assert out == "name,age\nAli,22\nSara,\n"


def test_field_order_follows_first_appearance():
    out = to_csv_text([{"b": 1, "a": 2}, {"c": 3, "a": 4}])
    assert out.splitlines()[0] == "b,a,c"


def test_fields_option_reorders_and_subsets():
    out = to_csv_text(
        [{"name": "Ali", "age": 22, "city": "Swabi"}],
        fields=["city", "name"],
    )
    assert out == "city,name\nSwabi,Ali\n"


def test_nested_dicts_flatten_to_dotted_keys():
    out = to_csv_text([{"name": "Ali", "address": {"city": "Swabi", "zip": 23430}}])
    assert out == "name,address.city,address.zip\nAli,Swabi,23430\n"


def test_no_flatten_writes_nested_as_json():
    out = to_csv_text(
        [{"name": "Ali", "tags": ["a", "b"]}],
        flatten_nested=False,
    )
    assert out == 'name,tags\nAli,"[""a"", ""b""]"\n'


def test_single_object_is_one_row():
    assert to_csv_text({"name": "Ali", "age": 22}) == "name,age\nAli,22\n"


def test_empty_list_is_empty_string():
    assert to_csv_text([]) == ""


def test_non_dict_row_raises():
    with pytest.raises(ValueError, match="must be a JSON object"):
        to_csv_text([{"a": 1}, "oops"])


def test_none_and_booleans():
    out = to_csv_text([{"a": None, "b": True, "c": False}])
    assert out == "a,b,c\n,true,false\n"


def test_custom_delimiter():
    out = to_csv_text([{"a": 1, "b": 2}], delimiter=";")
    assert out == "a;b\n1;2\n"


def test_flatten_helper():
    assert flatten({"a": {"b": {"c": 1}}, "d": 2}) == {"a.b.c": 1, "d": 2}
    assert flatten({"a": {}}) == {"a": ""}
    assert flatten("not a dict") == {}


def test_convert_json_text_parses_json():
    out = convert_json_text('[{"name": "Ali"}, {"name": "Sara", "age": 25}]')
    assert out == "name,age\nAli,\nSara,25\n"


def test_convert_json_text_rejects_bad_json():
    with pytest.raises(json.JSONDecodeError):
        convert_json_text("{not json")


def _run_cli(args, input_text=None):
    env = {"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"}
    return subprocess.run(
        [sys.executable, str(CLI)] + args,
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(ROOT),
    )


def test_cli_file_input(tmp_path):
    data = tmp_path / "in.json"
    data.write_text('[{"name": "Ali", "age": 22}]', encoding="utf-8")
    run = _run_cli([str(data)])
    assert run.returncode == 0, run.stderr
    assert run.stdout == "name,age\nAli,22\n"


def test_cli_stdin_and_fields():
    run = _run_cli(
        ["--fields", "age,name"],
        input_text='[{"name": "Ali", "age": 22}]',
    )
    assert run.returncode == 0, run.stderr
    assert run.stdout == "age,name\n22,Ali\n"


def test_cli_invalid_json_exits_1():
    run = _run_cli([], input_text="{oops")
    assert run.returncode == 1
    assert "invalid JSON" in run.stderr


def test_cli_missing_file_exits_1():
    run = _run_cli(["/does/not/exist.json"])
    assert run.returncode == 1
    assert "cannot read input" in run.stderr
