import sys
import os, shutil
import pytest
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


def test_16_run(mp_logger, clean_output):
    try:
        tima_mindif_processor(
            os.path.join(dirname, "test_data", "STA_Test"),
            os.path.join(dirname, "test_data", "STA_Test_MinDif"),
            output_dir,
        )
    except Exception:
        pytest.fail("Exception Caught running 1.6 Test")


def test_16_run_with_id_array(mp_logger, clean_output):
    try:
        tima_mindif_processor(
            os.path.join(dirname, "test_data", "STA_Test"),
            os.path.join(dirname, "test_data", "STA_Test_MinDif"),
            output_dir,
            generate_id_array=True,
        )
    except Exception:
        pytest.fail("Exception Caught running 1.6 Test with ID array")
