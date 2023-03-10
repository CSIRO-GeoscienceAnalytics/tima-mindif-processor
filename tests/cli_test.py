import pytest
from tima_mindif_processor.__main__ import parse_args


def test_parse_args_none():
    try:
        args = parse_args(None)
        pytest.fail("Arguments passed while missing required fields")
    except SystemExit:
        pass


def test_parse_args_one():
    try:
        args = parse_args(["test_data/STA_Test"])
        pytest.fail("Arguments passed while missing required fields")
    except SystemExit:
        pass


def test_parse_args_minimum():
    try:
        args = parse_args(["test_data/STA_Test", "test_data/STA_Test_MinDif"])
        assert (
            args.project_path == "test_data/STA_Test"
        ), "Project path not set from first argument"
        assert (
            args.mindif_root == "test_data/STA_Test_MinDif"
        ), "MinDif path not set from second argument"
    except SystemExit:
        pytest.fail(
            "Parse arguments failed with the minimum 2 required positional args"
        )
