import argparse
import sys
from loguru import logger
from . import utils

# from .tima_mindif_processor import tima_mindif_processor as tima14
from .tima_mindif_processor_16 import tima_mindif_processor as tima16


@logger.catch
def main():
    parser = argparse.ArgumentParser(description="Process TIMA data")
    parser.add_argument("project_path", type=str, help="Path to the TIMA project")
    parser.add_argument("mindif_root", type=str, help="Path to the MinDif root")
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        default="./",
        type=str,
        help="Path to the desired output folder",
    )
    parser.add_argument(
        "--tima_version",
        "-t",
        dest="tima_version",
        choices=["1.4", "1.6"],
        default="1.6",
        type=str,
        help="Version of TIMA default 1.6",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        default=True,
        type=bool,
        help="Prints more information about app progress.",
    )
    parser.add_argument(
        "--thumbs",
        dest="thumbnails",
        default=False,
        type=bool,
        help="Create thumbnails.",
    )
    args = parser.parse_args()

    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time}</green> <level>{message}</level>",
        level="INFO" if not args.verbose else "DEBUG",
    )

    utils.create_thumbnail = args.thumbnails

    if args.tima_version == "1.6":
        tima16(args.project_path, args.mindif_root, args.output)
    # else:
    #     tima14(args.project_path, args.mindif_root, args.output)


if __name__ == "__main__":
    main()
