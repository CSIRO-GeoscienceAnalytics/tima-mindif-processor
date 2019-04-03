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

Then

```
python tima_mindif_processor.py <Path to Zip File>
```

The results will go in a foler called "output"

## Troubleshooting

You may get a warning to delete the working directory manuelly after a successful run.
