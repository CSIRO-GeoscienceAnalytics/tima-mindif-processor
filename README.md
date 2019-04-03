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

If you get an error like:

```
WindowsError: [Error 32] The process cannot access the file because it is being used by another process: 'C:\\Users\\bra483\\dev\\python playground\\tima\\working\\f21dc551-bf0e-43d2-b5a6-f6990b340b92\\fields\\K07\\phases.tif'
```

Please ignore and delete the "working" folder manualy. WIll fix this at a later date.
