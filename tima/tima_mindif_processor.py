# The purpose of this script is to process a provided MinDIF dataset, and during the
# process carry out these actions:
#   1. Create a classification image in full resolution with a legend.
#
# The script should be executed in the following manner:
#   ./tima_mindif_processor.py project/path mindif_root output_root
#
# For example:
#   ./tima_mindif_processor.py "/media/sf_Y_DRIVE/Data/Evolution" "/media/sf_Y_DRIVE/Data/Adam Brown" "output"


import time
import signal
import os
import os.path
import sys
import math
import re
import copy
import multiprocessing
import numpy as np
from functools import partial
import xml.etree.ElementTree as ET
from loguru import logger
from PIL import Image, ImageDraw, ImageFont, ImageColor
from pathlib import Path

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
XML_NAMESPACE = None


class SampleError(Exception):
    pass


def get_percent_text(value):
    if value < 0.01:
        return "<0.01"
    return "{:4.2f}".format(value)


def set_global(logger_):
    global XML_NAMESPACE
    global logger
    logger = logger_
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if not XML_NAMESPACE:
        namespace = "http://www.tescan.cz/tima/1_4"
        XML_NAMESPACE = "{{{0}}}".format(namespace) if namespace else ""


def tima_mindif_processor(
    project_path: str,
    mindif_root: str,
    output_root: str,
    exclude_unclassified: bool = True,
    create_thumbnail: bool = False,
    show_low_val: bool = True,
    generate_id_array: bool = True,
    generate_bse: bool = True,
):
    start = time.time()
    proj_path = Path(project_path)
    project_name = proj_path.name

    logger.info("Project Name: {}", project_name)
    guid_and_sample_name = []

    is_16 = False
    data_file = ""
    struct_file = None
    for file in os.listdir(project_path):
        if file.endswith(".timaproj.data"):
            is_16 = True
            data_file = file
        if file.endswith(".timaproj.struct"):
            struct_file = file

    if is_16:
        if struct_file is None:
            sys.exit(
                "Could not find a file in the project folder ending with .timaproj.struct. "
                + "Please ensure project is a valid for TIMA 1.6+"
            )

        data_xml_path = os.path.join(project_path, data_file)
        logger.info(f"File {data_xml_path} exists, configuring for TIMA 1.6+")
        data_xml = ET.parse(data_xml_path)
        project_data = data_xml.getroot()

        rep_to_dir = {}
        for dataset in project_data.iterfind("DataSet"):
            rep_to_dir[dataset.findtext("Parent")] = dataset.findtext("DirName")

        struct_xml_path = os.path.join(project_path, struct_file)
        struct_xml = ET.parse(struct_xml_path)
        struct_data = struct_xml.getroot()

        # Get the names of the samples and the GUID that they're mapped to:
        survey_group = struct_data.find("SurveyGroup")
        if survey_group is not None:
            for survey in survey_group.iterfind("Survey"):
                for replicate in survey.iterfind("Replicate"):
                    guid = replicate.get("guid")
                    caption = replicate.get("caption")
                    if guid is not None and caption is not None and guid in rep_to_dir:
                        guid_and_sample_name.append((rep_to_dir[guid], caption))
                    else:
                        logger.warning(
                            "Something went wrong adding a sample to the list GUID: "
                            + "{}, Caption: {}",
                            guid,
                            caption,
                        )
                        logger.warning(
                            "Dataset {} may be missing from {}", guid, data_xml_path
                        )
        else:
            logger.error(
                "SurveryGroup element could not be found in {}", struct_xml_path
            )
    else:
        logger.info(
            f"No File {project_name}.timaproj.data file exists, configuring for TIMA 1.4"
        )
        surveys_xml_path = os.path.join(
            project_path, project_name + ".timaproj.Surveys", "Surveys.xml"
        )
        surveys_xml = ET.parse(surveys_xml_path)
        survey_group = surveys_xml.getroot()
        for survey in survey_group.iterfind("Survey"):
            for replicate in survey.iterfind("Replicate"):
                for dataset in replicate.iterfind("Dataset"):
                    guid_and_sample_name.append(
                        (dataset.get("guid")[1:37], replicate.get("caption"))
                    )
    func = partial(
        create_sample,
        mindif_root,
        output_root,
        exclude_unclassified,
        show_low_val,
        create_thumbnail,
        generate_id_array,
        generate_bse,
    )

    try:
        pool = multiprocessing.Pool(initializer=set_global, initargs=(logger,))
        pool.map(func, guid_and_sample_name)
        end = time.time()
        hours, rem = divmod(end - start, 3600)
        minutes, seconds = divmod(rem, 60)
        logger.info(
            "Tima MinDif Processor completed in {:0>2}:{:0>2}:{:05.2f}",
            int(hours),
            int(minutes),
            seconds,
        )
        logger.warning("Press Enter to terminate")
        input("")
    except KeyboardInterrupt:
        logger.warning("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
    else:
        logger.info("Sample processing complete")
        pool.close()  # Marks the pool as closed.
    finally:
        pool.join()


def create_sample(
    mindif_root: str,
    output_root: str,
    exclude_unclassified: bool,
    show_low_val: bool,
    create_thumbnail: bool,
    generate_id_array: bool,
    generate_bse: bool,
    guid_and_sample_name,
):

    start = time.time()
    guid = guid_and_sample_name[0]
    sample_name = guid_and_sample_name[1]

    logger.debug("Sample: {} started processing", sample_name)

    try:
        thumbnail_path = os.path.join(output_root, sample_name + ".thumbnail.png")
        classification_path = os.path.join(output_root, sample_name + ".png")

        if os.path.exists(classification_path):
            logger.info(
                "skipping {} because an image already exists for it.", sample_name
            )
            return

        if generate_bse:
            bse_path = os.path.join(output_root, sample_name + "_bse.png")
            if os.path.exists(bse_path):
                logger.info(
                    "Not generating bse png for sample {} because a file already exists for it.",
                    sample_name,
                )
                generate_bse = False

        if generate_id_array:
            id_array_path = os.path.join(output_root, sample_name + ".csv.gz")
            if os.path.exists(id_array_path):
                logger.info(
                    "Not generating id_array for sample {} because a csv already exists for it.",
                    sample_name,
                )
                generate_id_array = False

        mindif_path = os.path.join(mindif_root, guid)

        white = (255, 255, 255)
        black = (0, 0, 0)

        sample_name_font_size = 36
        font_size = 24
        font_path = os.path.join(SCRIPT_PATH, "fonts")
        sample_name_font = ImageFont.truetype(
            os.path.join(font_path, "DejaVuSansMono.ttf"), sample_name_font_size
        )
        font = ImageFont.truetype(
            os.path.join(font_path, "DejaVuSansMono.ttf"), font_size
        )

        sample_name_line_height = int(math.ceil(sample_name_font_size * 1.3))
        legend_text_y_offset = int(math.ceil(sample_name_line_height * 1.5))
        legend_line_height = int(math.ceil(font_size * 1.3))
        legend_text_x_offset = legend_line_height * 2 - font_size

        # Extract the phases from phases.xml and use it to create the colour map:
        xml_path = ""
        for root, dirs, files in os.walk(mindif_path):
            for file in files:
                if file == "phases.xml":
                    xml_path = root
                    break

            if xml_path:
                break

        if not xml_path:
            logger.warning(
                "phases.xml was not found in {} or the directory does not exist.",
                mindif_path,
            )
            return

        phases_xml_path = os.path.join(xml_path, "phases.xml")
        phases_xml = ET.parse(phases_xml_path)
        phase_nodes = phases_xml.getroot().find(
            "{0}PrimaryPhases".format(XML_NAMESPACE)
        )
        largest_name_width = 0
        phase_map = {}

        logger.debug("Extracting phases from {}", phases_xml_path)
        for phase_node in phase_nodes:
            mineral_name = phase_node.get("name")

            if (
                mineral_name == "[Unclassified]"
                or phase_node.get("background") == "yes"
            ) and exclude_unclassified:
                logger.debug("Excluding mineral {}", mineral_name)
                continue

            phase_id: str = phase_node.get("id", None)
            if phase_id is None:
                logger.wanring(f"Phase node {phase_node} is missing ID")
                continue

            largest_name_width = max(largest_name_width, font.getsize(mineral_name)[0])

            colour_str = phase_node.get("color")

            phase_map[int(phase_id)] = {
                "mineral_name": mineral_name,
                "colour": (
                    int(colour_str[1:3], 16),
                    int(colour_str[3:5], 16),
                    int(colour_str[5:7], 16),
                ),
                "colour_hex": colour_str,
                "mass": float(phase_node.get("mass")) if "mass" in phase_node else -1,
                "histogram": 0,
            }

        empty_phase_map = copy.deepcopy(phase_map)

        # Extract information from measurement.xml and create the mindif record:
        measurement_xml_path = os.path.join(xml_path, "measurement.xml")
        measurement_xml = ET.parse(measurement_xml_path)
        measurement_nodes = measurement_xml.getroot()

        measurement_guid = measurement_nodes.findtext("{0}Id".format(XML_NAMESPACE))
        measurement_guid = re.sub("[^[a-f0-9]", "", measurement_guid)

        software_version = measurement_nodes.findtext("{0}Origin".format(XML_NAMESPACE))
        logger.debug("Tima Software Version: {}", software_version)

        view_field_um = int(
            measurement_nodes.findtext("{0}ViewField".format(XML_NAMESPACE))
        )
        image_width_px = int(
            measurement_nodes.findtext("{0}ImageWidth".format(XML_NAMESPACE))
        )
        image_height_px = int(
            measurement_nodes.findtext("{0}ImageHeight".format(XML_NAMESPACE))
        )
        sample_shape = measurement_nodes.find(
            "{}SampleDef".format(XML_NAMESPACE)
        ).findtext("{0}SampleShape".format(XML_NAMESPACE))

        if sample_shape == "Rectangle":
            sample_width_um = int(
                measurement_nodes.find("{}SampleDef".format(XML_NAMESPACE)).findtext(
                    "{0}SampleWidth".format(XML_NAMESPACE)
                )
            )
            sample_height_um = int(
                measurement_nodes.find("{}SampleDef".format(XML_NAMESPACE)).findtext(
                    "{0}SampleHeight".format(XML_NAMESPACE)
                )
            )
            sample_width_px = int(
                (sample_width_um / float(view_field_um)) * image_width_px
            )
            sample_height_px = int(
                (sample_height_um / float(view_field_um)) * image_height_px
            )
            field_size = (sample_width_px, sample_height_px)

        else:
            # Must be a circle
            sample_diameter_um = int(
                measurement_nodes.find("{}SampleDef".format(XML_NAMESPACE)).findtext(
                    "{0}SampleDiameter".format(XML_NAMESPACE)
                )
            )
            diameter_px = int(
                (sample_diameter_um / float(view_field_um)) * image_width_px
            )
            field_size = (diameter_px, diameter_px)

        # To right-align the numeric values we use "< 0.01" as the longest string then work out the offset
        # from that.
        max_numeric_width = font.getsize("<0.01")[0]
        legend_start_x = int(math.ceil(field_size[0] + 30))

        # this is the x value that the numeric value must STOP at.
        percent_right_x = (
            field_size[0]
            + legend_text_x_offset
            + largest_name_width
            + max_numeric_width
            + legend_line_height
            - font_size
        )
        canvas_size = (percent_right_x, field_size[1])
        # outline_thickness = math.ceil(field_size[0] / 1000)
        origin = (field_size[0] / 2, field_size[1] / 2)
        pixel_spacing = float(view_field_um) / float(image_width_px)

        # Extract the field information from fields.xml:
        fields_xml_path = os.path.join(xml_path, "fields.xml")
        fields_xml = ET.parse(fields_xml_path)
        fields_xml_root = fields_xml.getroot()
        field_nodes = fields_xml_root.find("{}Fields".format(XML_NAMESPACE))
        field_dir = fields_xml_root.findtext("{}FieldDir".format(XML_NAMESPACE))

        fields = []
        if field_nodes is not None:
            for field_node in field_nodes:
                field_name = field_node.get("name")

                # The x and y values are the offset from the origin.
                # TIMA uses +x to mean left, which is opposite to monitor coordinate system,
                # so this value gets inverted.
                # and       +y to mean down, which is the same as monitor coordinate system,
                # so this value doesn't get inverted.
                x = math.floor(
                    -float(field_node.get("x")) / pixel_spacing
                    + origin[0]
                    - (image_width_px / 2)
                )
                y = math.floor(
                    float(field_node.get("y")) / pixel_spacing
                    + origin[1]
                    - (image_height_px / 2)
                )

                fields.append((field_name, x, y))
        else:
            logger.warning(
                "{}, {}  does not have any Fields in the fields.xml file",
                guid,
                sample_name,
            )

        # Prepare new canvas:
        png = Image.new("RGB", canvas_size, white)
        png_array = png.load()

        if generate_bse:
            bse_png = Image.new("I;16", field_size, 65535)
            bse_png_array = bse_png.load()

        if generate_id_array:
            phase_id_array = np.full(field_size, -1)

        classified_pixel_count = 0

        field_path_format = os.path.join(xml_path, field_dir, "{0}", "{1}")

        thumbnail_x_min = 1000000000
        thumbnail_x_max = -1
        thumbnail_y_min = 1000000000
        thumbnail_y_max = -1

        for field_name, field_x, field_y in fields:
            field_phase_map = copy.deepcopy(empty_phase_map)
            has_missing_file = False
            has_missing_bse = False
            try:
                phases = Image.open(field_path_format.format(field_name, "phases.tif"))
            except Exception:
                logger.error(
                    "Error: {}, {}, field {} does not have phases.tif",
                    guid,
                    sample_name,
                    field_name,
                )
                has_missing_file = True

            try:
                mask = Image.open(field_path_format.format(field_name, "mask.png"))
            except Exception:
                logger.error(
                    "Error: {}, {}, field {} does not have mask.png",
                    guid,
                    sample_name,
                    field_name,
                )
                has_missing_file = True

            if generate_bse:
                try:
                    bse = Image.open(field_path_format.format(field_name, "bse.png"))
                    bse_array = bse.load()
                except Exception:
                    logger.error(
                        "Error: {}, {}, field {} does not have bse.png",
                        guid,
                        sample_name,
                        field_name,
                    )
                    has_missing_bse = True

            if has_missing_file:
                continue

            phases_array = phases.load()
            mask_array = mask.load()
            # if field_y == 2050:
            #     print("Mask is 0")
            unk_count = 0
            error_count = 0

            for y in range(0, image_height_px):
                for x in range(0, image_width_px):
                    try:
                        phase_index: int = int(phases_array[x, y])

                        mask_index = mask_array[
                            x, y
                        ]  # For some reason mask is reversed
                        png_x = x + field_x
                        png_y = y + field_y

                        if generate_bse and not has_missing_bse:
                            bse_png_array[png_x, png_y] = bse_array[x, y]

                        if phase_index == 0 and mask_index != 0:
                            unk_count += 1

                        if (
                            phase_index != 0 or not exclude_unclassified
                        ) and mask_index != 0:
                            if phase_map.get(phase_index, None) is None:
                                error_count += 1
                                if error_count == 1:
                                    logger.error(
                                        f"Phase index {phase_index} is missing in sample: {sample_name}, guid: {guid}, field: {field_name}\nPlease Check your phases file {phases_xml_path}\nNote you will only see this error once per sample"
                                    )

                                if error_count == 1:
                                    logger.debug(phase_map)

                                if error_count > 25:
                                    raise SampleError()

                                continue

                            png_array[png_x, png_y] = phase_map[phase_index]["colour"]

                            if generate_id_array:
                                phase_id_array[y + field_y, x + field_x] = phase_index

                            thumbnail_x_min = min(thumbnail_x_min, png_x)
                            thumbnail_x_max = max(thumbnail_x_max, png_x)
                            thumbnail_y_min = min(thumbnail_y_min, png_y)
                            thumbnail_y_max = max(thumbnail_y_max, png_y)

                            classified_pixel_count += 1
                            phase_map[phase_index]["histogram"] += 1
                            field_phase_map[phase_index]["histogram"] += 1
                    except IndexError:
                        logger.error(
                            "Index out of bounds in phase/mask loop x: {} y: {}", x, y
                        )
                        break

            if error_count > 0:
                logger.warning(
                    f"Skipped {error_count} pixels for {sample_name} due to errors."
                )
            UNK_THRESHOLD_PC = 15
            UNK_THRESHOLD = int(x * y * (UNK_THRESHOLD_PC / 100))  # 15%
            if unk_count > UNK_THRESHOLD:
                logger.warning(
                    f"Sample: {sample_name} Field: {field_name} GUID: {guid} contains greater than {UNK_THRESHOLD_PC}% of Unclassified."
                )
            # Once all the pixels have been dealt with we can create the insert commands for this field:
            field_phase_map = {
                k: v for k, v in field_phase_map.items() if v["histogram"] != 0
            }

            field_phase_map = sorted(
                field_phase_map.items(), key=lambda x: x[1]["histogram"], reverse=True
            )

        if has_missing_file:
            logger.warning("Warning: sample {} is missing fields.", sample_name)
            # return

        # Remove phase_map entries where histogram == 0
        phase_map = {k: v for k, v in phase_map.items() if v["histogram"] != 0}

        # Sort phase_map entries by histogram highest to lowest
        phase_map = sorted(
            phase_map.items(), key=lambda x: x[1]["histogram"], reverse=True
        )

        draw = ImageDraw.Draw(png)
        draw.text(
            (legend_start_x, 5), sample_name, black, font=sample_name_font,
        )
        y = legend_text_y_offset
        for id, phase_map_entry in phase_map:
            if not show_low_val and (
                (float(phase_map_entry["histogram"]) / classified_pixel_count * 100)
                < 0.01
            ):
                continue

            draw.rectangle(
                [
                    (legend_start_x, y),
                    (legend_start_x + legend_line_height, y + legend_line_height),
                ],
                fill=phase_map_entry["colour"],
            )
            draw.text(
                (legend_start_x + legend_text_x_offset, y),
                phase_map_entry["mineral_name"],
                black,
                font=font,
            )
            text = get_percent_text(
                float(phase_map_entry["histogram"]) / classified_pixel_count * 100
            )
            draw.text(
                (percent_right_x - font.getsize(text)[0], y), text, black, font=font
            )
            y += legend_line_height

        if not os.path.exists(output_root):
            os.makedirs(output_root)

        if create_thumbnail:
            thumbnail_bbox = (
                int(thumbnail_x_min),
                int(thumbnail_y_min),
                int(thumbnail_x_max),
                int(thumbnail_y_max),
            )
            thumbnail_png = png.crop(thumbnail_bbox)
            thumbnail_png.load()
            thumbnail_png.thumbnail((300, 300), Image.ANTIALIAS)
            thumbnail_png.save(thumbnail_path)
            logger.debug(
                "Sample: {} thumbnail saved to {}", sample_name, thumbnail_path
            )
            del thumbnail_png

        # Add the circle to the original image and save
        # draw.arc([0, 0, field_size[0], field_size[1]], 0, 360, black)
        png.save(classification_path)
        logger.debug("Sample: {} image saved to {}", sample_name, classification_path)

        if generate_bse:
            bse_png.save(bse_path)
            logger.debug("Sample: {} BSE image saved to {}", sample_name, bse_path)
            del bse_png

        if generate_id_array:
            np.savetxt(
                id_array_path,
                phase_id_array,
                fmt="%d",
                delimiter=",",
                newline="\n",
                header="",
                footer="",
            )
            logger.debug("Sample: {} id array saved to {}", sample_name, id_array_path)

        end = time.time()
        logger.info(
            "Sample: {} completed processing in {:.1f} Seconds",
            sample_name,
            end - start,
        )
        del draw
        del png
    except SampleError:
        logger.error(
            f"Exceeded error threshold on Sample: {sample_name} GUID: {guid}, skipping."
        )
