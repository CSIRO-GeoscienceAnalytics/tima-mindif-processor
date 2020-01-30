import time
import argparse
import sys
import os
from loguru import logger

# from .tima_mindif_processor import tima_mindif_processor as tima14
from .tima_mindif_processor import tima_mindif_processor


def parse_args(args):
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
        "--verbose",
        action="store_true",
        help="Prints more information about app progress.",
    )
    parser.add_argument(
        "--exclude-unclassified",
        "-u",
        action="store_true",
        help="Exclude unclassified rock types from image",
    )
    parser.add_argument(
        "--show-low-val",
        "-l",
        action="store_true",
        help="Prints rock types with <0.01 in the legend.",
    )
    parser.add_argument(
        "--id-arrays",
        "-i",
        action="store_true",
        help="Generate Rock Type ID Arrays for each sample.",
    )
    parser.add_argument(
        "--bse",
        "-b",
        action="store_true",
        help="Generate the stitched together BSE image.",
    )
    parser.add_argument("--thumbs", action="store_true", help="Create thumbnails.")
    return parser.parse_args(args)


@logger.catch
def main():
    args = parse_args(sys.argv[1:])
    logger.remove()

    logger.add(
        sys.stdout,
        enqueue=True,
        level="INFO" if not args.verbose else "DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <cyan>{process}</cyan> | <level>{message}</level>",
    )

    if not os.path.exists(args.project_path):
        logger.error("Could not find: {}", args.project_path)
        return

    if not os.path.exists(args.mindif_root):
        logger.error("Could not find: {}", args.mindif_root)
        return

    exclude_unclassified: bool = True if args.exclude_unclassified else False
    show_low_val: bool = True if args.show_low_val else False
    id_arrays: bool = True if args.id_arrays else False
    create_thumbnail: bool = True if args.thumbs else False
    generate_bse: bool = True if args.bse else False

    logger.info("Starting Tima MinDif Processor with the following settings")
    logger.info("Project Path: {}", args.project_path)
    logger.info("MinDif Path: {}", args.mindif_root)
    logger.info("Output Directory: {}", args.output)
    logger.info("Exclude Unclassified: {}", exclude_unclassified)
    logger.info("Show Low Values in Legend: {}", show_low_val)
    logger.info("Generate Rock Type ID Arrays: {}", id_arrays)

    tima_mindif_processor(
        args.project_path,
        args.mindif_root,
        output_root=args.output,
        exclude_unclassified=exclude_unclassified,
        show_low_val=show_low_val,
        create_thumbnail=create_thumbnail,
        generate_id_array=id_arrays,
        generate_bse=generate_bse,
    )


if __name__ == "__main__":
    main()
