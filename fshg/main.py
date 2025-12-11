"""FourXSix Headshot Generator (fshg) command line interface."""

import argparse

from .fshg import create_photo_sheet
from .fshg import PhotoSheetLayout


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
    parser.add_argument(
        "--dpi",
        type=int,
        default=1000,
        help="Dots per inch for the output image (default: 1000)",
    )
    parser.add_argument(
        "--layout",
        choices=["1inch", "2inch"],
        default="1inch",
        help="Photo layout size (default: 1inch)",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=0,
        help="Gap in pixels between photos (default: 0)",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=2,
        help="Width of the cutting border in pixels (default: 2)",
    )
    parser.add_argument(
        "--color",
        default="#CCCCCC",
        help="Color of the cutting border (default: #CCCCCC)",
    )

    args = parser.parse_args()

    layout_map = {
        "1inch": PhotoSheetLayout.ONE_INCH_TAIWAN,
        "2inch": PhotoSheetLayout.TWO_INCH_TAIWAN,
    }

    create_photo_sheet(
        args.input,
        args.output,
        dpi=args.dpi,
        photo_layout=layout_map[args.layout],
        gap=args.gap,
        border_w=args.border,
        border_color=args.color,
    )
