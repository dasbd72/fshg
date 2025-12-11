"""FourXSix Headshot Generator (fshg) command line interface."""

import argparse

from .fshg import create_photo_sheet


def main():
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        prog="fshg",
        description=(
            "Layout a 1-inch photo onto a 4x6 canvas for printing at 7-11."
        ),
    )

    parser.add_argument(
        "input",
        help="Path to the input image file (e.g., input.jpg)",
    )
    parser.add_argument(
        "output",
        help="Path to save the output image file (e.g., output.jpg)",
    )

    args = parser.parse_args()

    create_photo_sheet(args.input, args.output)
