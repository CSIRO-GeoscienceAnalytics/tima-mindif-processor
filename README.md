# TIMA Mindif Processor

## Getting Started

To run make sure you have conda installed, only do these step once. Using the command line (preferably GitBash) at the project root.

```
conda env create -f environment.yml
```

## Usage

Using the command line at the project root.

```
source activate tima
```

Or if that doesn't work

```
conda activate tima
```

The script should be executed in the following manner:
python tima_mindif_processor.py project/path mindif_root output_root

For example:

```
python tima_mindif_processor.py "/media/sf_Y_DRIVE/Data/Evolution" "/media/sf_Y_DRIVE/Data/Adam Brown" "output"
```
