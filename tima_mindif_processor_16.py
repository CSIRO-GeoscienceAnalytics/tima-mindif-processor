#!/usr/bin/python

# The purpose of this script is to process a provided MinDIF dataset, and during the process carry out these actions:
#   1. Create a classification image in full resolution with a legend.
#
# The script should be executed in the following manner:
#   ./tima_mindif_processor.py project/path mindif_root output_root
#
# For example:
#   ./tima_mindif_processor.py "/media/sf_Y_DRIVE/Data/Evolution" "/media/sf_Y_DRIVE/Data/Adam Brown" "output"

import os
import os.path
import sys
import math
import re
import copy
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

verbose = True
create_thumbnail = False

script_path = os.path.dirname(os.path.realpath(__file__))

# Helper methods:


def log_variable(name, value):
    if verbose:
        print("{0}: {1}".format(name, value))


def log_message(message):
    if verbose:
        print(message)


def get_percent_text(value):
    if value < 0.01:
        return "<0.01"
    return "{:4.2f}".format(value)


# Parse arguments:
project_path = sys.argv[1]
mindif_root = sys.argv[2]
output_root = sys.argv[3]
project_name = os.path.split(project_path)[1]

print "Project Name: {}".format(project_name)

data_xml_path = os.path.join(
    project_path, project_name + '.timaproj.data')
data_xml = ET.parse(data_xml_path)
project_data = data_xml.getroot()

# Get the names of the samples and the GUID that they're mapped to:
guid_and_sample_name = {}
for dataset in project_data.iterfind('DataSet'):
    guid_and_sample_name[dataset.find(
        'GUID').text[1:37]] = dataset.find('JobName').text

for guid, sample_name in guid_and_sample_name.iteritems():
    log_variable("Sample Name", sample_name)
    thumbnail_path = os.path.join(output_root, sample_name + '.thumbnail.png')
    classification_path = os.path.join(output_root, sample_name + '.png')

    if os.path.exists(classification_path):
        print("NOTICE: skipping " + guid +
              " because an image already exists for it.")
        continue

    mindif_path = os.path.join(mindif_root, guid)

    # Constants / Readonly:
    # namespace = 'http://www.tescan.cz/tima/1_4'  # TODO: make namespace dynamic
    # xml_namespace = '{{{0}}}'.format(namespace) if namespace else ''

    # namespaces = {'tescan': namespace}
    white = (255, 255, 255)
    black = (0, 0, 0)

    font_size = 24
    font_path = os.path.join(script_path, 'fonts')
    font = ImageFont.truetype(os.path.join(
        font_path, 'DejaVuSansMono.ttf'), font_size)

    legend_line_height = int(math.ceil(font_size * 1.3))
    legend_text_x_offset = legend_line_height * 2 - font_size

    log_variable('Font Size', font_size)
    log_variable('Legend Line Height', legend_line_height)
    log_variable('Legend text X Offset', legend_text_x_offset)

    # Extract the phases from phases.xml and use it to create the colour map:
    xml_path = ''
    for root, dirs, files in os.walk(mindif_path):
        for file in files:
            if file == "phases.xml":
                xml_path = root
                break

        if xml_path:
            break

    if not xml_path:
        print("WARNING: phases.xml was not found in " +
              mindif_path + " or the directory does not exist.")
        continue

    phases_xml_path = os.path.join(xml_path, "phases.xml")
    phases_xml = ET.parse(phases_xml_path)
    phase_nodes = phases_xml.getroot().find('Phases')
    largest_name_width = 0
    phase_map = {}

    log_message('Extracting phases from {0}'.format(phases_xml_path))
    for phase_node in phase_nodes.iterfind('Phase'):
        mineral_name = phase_node.get('Caption')

        # if phase_node.get('background') == 'yes' or mineral_name == '[Unclassified]':
        if mineral_name == '[Unclassified]':
            continue

        phase_id = int(phase_node.get('id'))

        largest_name_width = max(
            largest_name_width, font.getsize(mineral_name)[0])

        colour_str = phase_node.find('Color').text
        mass = float(phase_node.find('Density').text)

        phase_map[phase_id] = {
            'mineral_name': mineral_name,
            'colour': (
                int(colour_str[1:3], 16),
                int(colour_str[3:5], 16),
                int(colour_str[5:7], 16)),
            'colour_hex': colour_str,
            'mass': mass,
            'histogram': 0
        }

    empty_phase_map = copy.deepcopy(phase_map)

    # Extract information from measurement.xml and create the mindif record:
    profile_xml_path = os.path.join(mindif_path, 'index.xml')
    profile_xml = ET.parse(profile_xml_path)
    profile_nodes = profile_xml.getroot()

    measurement_guid = profile_nodes.get('GUID')
    measurement_guid = re.sub('[^[a-f0-9]', '', measurement_guid)

    info_node = profile_nodes.find("Info")

    software_version = info_node.findtext('Origin')
    view_field_um = int(info_node.findtext('FieldWidth'))
    image_width_px = int(info_node.findtext('ImageWidth'))
    image_height_px = int(info_node.findtext('ImageHeight'))
    sample_shape = info_node.find('Sample').findtext('Shape')

    if sample_shape == "Rectangle":
        sample_width_um = int((float(info_node.find('Sample').findtext('Right')) - float(info_node.find('Sample').findtext('Left'))) * 1000)
        sample_height_um = int((float(info_node.find('Sample').findtext('Bottom')) - float(info_node.find('Sample').findtext('Top'))) * 1000)
        sample_width_px = int(
            (sample_width_um / float(view_field_um)) * image_width_px)
        sample_height_px = int(
            (sample_height_um / float(view_field_um)) * image_height_px)
        field_size = (sample_width_px, sample_height_px)

    else:
        # Must be a circle
        sample_diameter_um = int((float(info_node.find('Sample').findtext('Right')) - float(info_node.find('Sample').findtext('Left'))) * 1000)
        diameter_px = int((sample_diameter_um / float(view_field_um)) * image_width_px)
        field_size=(diameter_px, diameter_px)

    # To right-align the numeric values we use "< 0.01" as the longest string then work out the offset from that.
    max_numeric_width=font.getsize("<0.01")[0]
    legend_start_x=int(math.ceil(field_size[0] + 30))

    # this is the x value that the numeric value must STOP at.
    percent_right_x=field_size[0] + legend_text_x_offset + \
        largest_name_width + max_numeric_width + legend_line_height - font_size
    canvas_size=(percent_right_x, field_size[1])
    outline_thickness=math.ceil(field_size[0] / 1000)
    origin=(field_size[0]/2, field_size[1]/2)
    pixel_spacing=float(view_field_um) / float(image_width_px)

    # Extract the field information from fields.xml:
    fields_node = profile_nodes.find("Fields")
    field_dir = fields_node.get("dirName")
    field_nodes = fields_node.findall("Field")

    fields=[]
    if field_nodes is not None:
        for field_node in field_nodes:
            field_name=field_node.findtext('Path')

            # The x and y values are the offset from the origin.
            # TIMA uses +x to mean left, which is opposite to monitor coordinate system, so this value gets inverted.
            # and       +y to mean down, which is the same as monitor coordinate system, so this value doesn't get inverted.
            x=round(-float(float(field_node.findtext('StageX')) * 1000) / pixel_spacing +
                      origin[0] - (image_width_px / 2))
            y=round(float(float(field_node.findtext('StageY')) * 1000) / pixel_spacing +
                      origin[1] - (image_height_px / 2))

            fields.append((field_name, x, y))
    else:
        print('WARNING: ' + guid + ", " + sample_name +
              ' does not have any tescan:Fields in the index.xml file')

    #FIXME THis is where I got up to

    # Prepare new canvas:
    png = Image.new('RGB', canvas_size, white)
    png_array = png.load()

    classified_pixel_count = 0

    field_path_format = os.path.join(xml_path, field_dir, '{0}', '{1}')

    thumbnail_x_min = 1000000000
    thumbnail_x_max = -1
    thumbnail_y_min = 1000000000
    thumbnail_y_max = -1

    has_missing_file = False
    for field_name, field_x, field_y in fields:
        field_phase_map = copy.deepcopy(empty_phase_map)

        try:
            phases = Image.open(
                field_path_format.format(field_name, 'phases.tif'))
        except:
            print('Error: ' + guid + ", " + sample_name + ', field ' +
                  field_name + " does not have phases.tif")
            has_missing_file = True

        try:
            mask = Image.open(field_path_format.format(field_name, 'mask.png'))
        except:
            print('Error: ' + guid + ", " + sample_name +
                  ', field ' + field_name + " does not have mask.png")
            has_missing_file = True

        if has_missing_file:
            continue

        phases_array = phases.load()
        mask_array = mask.load()

        for y in range(0, image_height_px):
            for x in range(0, image_width_px):
                try:
                    phase_index = phases_array[x, y]
                    mask_index = mask_array[x, y]
                    if phase_index != 0 and mask_index != 0:
                        png_x = x + field_x
                        png_y = y + field_y

                        png_array[x + field_x, y +
                                  field_y] = phase_map[phase_index]['colour']

                        thumbnail_x_min = min(thumbnail_x_min, png_x)
                        thumbnail_x_max = max(thumbnail_x_max, png_x)
                        thumbnail_y_min = min(thumbnail_y_min, png_y)
                        thumbnail_y_max = max(thumbnail_y_max, png_y)

                        classified_pixel_count += 1
                        phase_map[phase_index]['histogram'] += 1
                        field_phase_map[phase_index]['histogram'] += 1
                except IndexError as exc:
                    print "Index out of bounds in phase/mask loop x: {} y: {}".format(
                        x, y)
                    break

        # Once all the pixels have been dealt with we can create the insert commands for this field:
        field_phase_map = {
            k: v for k, v in field_phase_map.iteritems() if v['histogram'] != 0}

        # TODO: this is a waste, all I really want to do is change from dict to list
        field_phase_map = sorted(field_phase_map.items(
        ), key=lambda x: x[1]['histogram'], reverse=True)

    if has_missing_file:
        print('Error: not processing ' + guid + ' due to missing files.')
        continue

    # Remove phase_map entries where histogram == 0
    phase_map = {k: v for k, v in phase_map.iteritems() if v['histogram'] != 0}

    # Sort phase_map entries by histogram highest to lowest
    phase_map = sorted(phase_map.items(),
                       key=lambda x: x[1]['histogram'], reverse=True)

    draw = ImageDraw.Draw(png)

    y = 0
    for id, phase_map_entry in phase_map:
        draw.rectangle([(legend_start_x, y), (legend_start_x + legend_line_height,
                                              y + legend_line_height)], fill=phase_map_entry['colour'])
        draw.text((legend_start_x + legend_text_x_offset, y),
                  phase_map_entry['mineral_name'], black, font=font)
        text = get_percent_text(
            float(phase_map_entry['histogram']) / classified_pixel_count * 100)
        draw.text((percent_right_x - font.getsize(text)
                   [0], y), text, black, font=font)
        y += legend_line_height

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    if create_thumbnail:
        thumbnail_bbox = (int(thumbnail_x_min), int(
            thumbnail_y_min), int(thumbnail_x_max), int(thumbnail_y_max))
        thumbnail_png = png.crop(thumbnail_bbox)
        thumbnail_png.load()
        thumbnail_png.thumbnail((300, 300), Image.ANTIALIAS)
        thumbnail_png.save(thumbnail_path)
        del thumbnail_png

    # Add the circle to the original image and save
    # draw.arc([0, 0, field_size[0], field_size[1]], 0, 360, black)
    png.save(classification_path)

    del draw
    del png
