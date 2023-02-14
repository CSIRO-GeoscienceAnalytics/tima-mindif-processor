# TIMA Mindif Processor

## Getting Started

install from pypi

```
pip install tima-mindef
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

Once it's installed use the command 'tima-mindef'

```
tima-mindef -h

usage: tima-mindef [-h] [--output OUTPUT] [--tima-version {1.4,1.5,1.6}]
                   [--verbose] [--thumbs]
                   project_path mindif_root

Process TIMA data

positional arguments:
  project_path          Path to the TIMA project
  mindif_root           Path to the MinDif root

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Path to the desired output folder
  --tima-version {1.4,1.5,1.6}, -t {1.4,1.5,1.6}
                        Version of TIMA default 1.6
  --verbose             Prints more information about app progress.
  --thumbs              Create thumbnails.

```

The script should be executed in the following manner:
tima-mindef tima_mindif_processor.py project/path mindif_root output_root

For example:

```
tima-mindef "/media/sf_Y_DRIVE/Data/Evolution" "/media/sf_Y_DRIVE/Data/Adam Brown" -o ./output
```
