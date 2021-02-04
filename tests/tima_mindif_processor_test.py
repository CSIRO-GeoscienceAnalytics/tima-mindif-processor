import sys
import os, shutil
import pytest
import mock
from loguru import logger
from tima.tima_mindif_processor import tima_mindif_processor

dirname = os.path.dirname(__file__)
output_dir = os.path.join(dirname, "test_output")


def rf_dir(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


@pytest.fixture
def clean_output():
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    rf_dir(output_dir)


@pytest.fixture
def mp_logger():
    logger.remove()

    logger.add(
        sys.stdout,
        enqueue=True,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <cyan>{process}</cyan> | <level>{message}</level>",
    )


def test_21_run(mp_logger, clean_output):
    with mock.patch("builtins.input", return_value="yes"):
        try:
            tima_mindif_processor(
                os.path.join(dirname, "test_data", "ERD_21_Test"),
                os.path.join(dirname, "test_data", "ERD_21_Test_MinDif"),
                output_dir,
                exclude_unclassified=False,
                create_thumbnail=False,
                generate_id_array=False,
                generate_bse=False,
            )
        except Exception:
            pytest.fail("Exception Caught running 2.1 Test")


def test_16_run(mp_logger, clean_output):
    with mock.patch("builtins.input", return_value="yes"):
        try:
            tima_mindif_processor(
                os.path.join(dirname, "test_data", "STA_Test"),
                os.path.join(dirname, "test_data", "STA_Test_MinDif"),
                output_dir,
                create_thumbnail=False,
                generate_id_array=False,
                generate_bse=False,
            )
        except Exception:
            pytest.fail("Exception Caught running 1.6 Test")


def test_16_run_with_id_array(mp_logger, clean_output):
    with mock.patch("builtins.input", return_value="yes"):
        try:
            tima_mindif_processor(
                os.path.join(dirname, "test_data", "STA_Test"),
                os.path.join(dirname, "test_data", "STA_Test_MinDif"),
                output_dir,
                create_thumbnail=True,
                generate_id_array=True,
                generate_bse=True,
            )
        except Exception:
            pytest.fail("Exception Caught running 1.6 Test with ID array")


def test_16_run_debug(mp_logger, clean_output):
    with mock.patch("builtins.input", return_value="yes"):
        try:
            tima_mindif_processor(
                os.path.join(dirname, "test_data", "Cloncurry METAL"),
                os.path.join(dirname, "test_data", "Cloncurry METAL_MinDif"),
                output_dir,
                exclude_unclassified=False,
                create_thumbnail=False,
                generate_id_array=False,
                generate_bse=False,
            )
        except Exception:
            pytest.fail("Exception Caught running 1.6 Test")
