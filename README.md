# TIMA Mindif Processor v2.0.1

[![PyPI version](https://badge.fury.io/py/tima-mindif.svg)](https://badge.fury.io/py/tima-mindif)

# Tima Mindif Processor

Processes a Tescan TIMA Mindif file to generate a classification panorama.

## Getting Started

install from pypi

```
pip install tima-mindif
```

Install direct from git (Note: this is currently a private repository)

```
pip install git+https://gitlab.com/csiro-geoanalytics/tima-utils/tima-mindif-processor.git
```

Or clone the repo so you can make changes or view the code, note the -e in the pip install is optional, it makes it so any code changes are automatically picked up.

```
git clone https://gitlab.com/csiro-geoanalytics/tima-utils/tima-mindif-processor.git
<Navigate to the code directory>
pip install -e .
```

If you would like to work on the code in a virtual env a pipfile is available

```
pip install pipenv
pipenv install
pipenv shell
```

## Usage

Once it's installed use the command 'tima-mindif'

```
tima-mindif -h

usage: tima-mindif [-h] [--output OUTPUT] [--verbose] [--exclude-unclassified] [--show-low-val] [--id-arrays] [--bse] [--thumbs] project_path mindif_root

Process TIMA data

positional arguments:
  project_path          Path to the TIMA project
  mindif_root           Path to the MinDif root

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Path to the desired output folder
  --verbose             Prints more information about app progress.
  --exclude-unclassified, -u
                        Exclude unclassified rock types from image
  --show-low-val, -l    Prints rock types with <0.01 in the legend.
  --id-arrays, -i       Generate Rock Type ID Arrays for each sample.
  --bse, -b             Generate the stitched together BSE image.
  --thumbs              Create thumbnails.

```

The script should be executed in the following manner:
tima-mindif project/path mindif_root output_root

For example:

```
tima-mindif "/media/sf_Y_DRIVE/Data/Evolution" "/media/sf_Y_DRIVE/Data/Adam Brown" -o ./output
```
