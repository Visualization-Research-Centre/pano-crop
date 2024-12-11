#!/bin/bash

set -e

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate the virtual environment
source venv/bin/activate

# Run the Python script
python main.py --csv files.csv --input_folder "./pano_pairs" --output_folder "./output"