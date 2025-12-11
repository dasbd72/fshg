"""FourXSix Headshot Generator (fshg) main module."""

from enum import Enum
import os
import sys
import tkinter as tk

from PIL import Image
from PIL import ImageOps
from PIL import ImageTk


class PhotoSheetLayout(Enum):
    ONE_INCH_TAIWAN = (2.8, 3.5)  # cm
    TWO_INCH_TAIWAN = (3.5, 4.5)  # cm


class AspectCropDialog:
    """Dialog for interactively cropping an image to a
    specified aspect ratio."""

    def __init__(self, pil_image, aspect_ratio):
        self._root = tk.Tk()
        self._root.title(
            "Crop Photo: Left-Click to Move, Right-Click/Scroll to Resize,"
            " ENTER to Confirm"
        )

        # Setup Image Display (Scale to fit screen)
        screen_w, screen_h = 900, 900
        orig_w, orig_h = pil_image.size
        self._scale = min(screen_w / orig_w, screen_h / orig_h, 1.0)

        display_size = (
            int(orig_w * self._scale),
            int(orig_h * self._scale),
        )
        display_image = pil_image.resize(display_size, Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(display_image)

        # Setup Canvas
        self._canvas = tk.Canvas(
            self._root,
            width=display_size[0],
            height=display_size[1],
            cursor="fleur",
        )
        self._canvas.pack()
        self._canvas.create_image(0, 0, image=self._photo, anchor="nw")

        # Setup Crop Box (Initial size: 50% of screen, centered)
        self._aspect_ratio = aspect_ratio  # width / height

        init_h = display_size[1] * 0.5
        init_w = init_h * self._aspect_ratio

        # Center coordinates
        cx, cy = display_size[0] / 2, display_size[1] / 2

        # Initial box coords (x1, y1, x2, y2)
        self._box_x1 = cx - init_w / 2
        self._box_y1 = cy - init_h / 2
        self._box_x2 = cx + init_w / 2
        self._box_y2 = cy + init_h / 2

        # Outer rectangle
        self._rect_id = self._canvas.create_rectangle(
            self._box_x1,
            self._box_y1,
            self._box_x2,
            self._box_y2,
            outline="red",
            width=2,
            dash=(10, 10),
        )
        # Horizontal line (for reference)
        self._hori_id = self._canvas.create_line(
            self._box_x1,
            (self._box_y1 + self._box_y2) / 2,
            self._box_x2,
            (self._box_y1 + self._box_y2) / 2,
            fill="red",
            dash=(5, 5),
        )
        # Vertical line (for reference)
        self._vert_id = self._canvas.create_line(
            (self._box_x1 + self._box_x2) / 2,
            self._box_y1,
            (self._box_x1 + self._box_x2) / 2,
            self._box_y2,
            fill="red",
            dash=(5, 5),
        )

        self.final_crop_box = (
            0,
            0,
            0,
            0,  # Will store (x1,y1,x2,y2) relative to original image
        )

        # Bind Events
        self._canvas.bind("<ButtonPress-1>", self._on_click)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind(
            "<ButtonPress-3>", self._on_click_resize
        )  # Right click start
        self._canvas.bind(
            "<B3-Motion>", self._on_drag_resize
        )  # Right click drag
        self._canvas.bind("<MouseWheel>", self._on_scroll)  # Windows Scroll
        self._canvas.bind("<Button-4>", self._on_scroll)  # Linux Scroll Up
        self._canvas.bind("<Button-5>", self._on_scroll)  # Linux Scroll Down
        self._root.bind("<Return>", self._on_finish)

        self._last_x = 0
        self._last_y = 0

    def run(self):
        self._root.mainloop()

    def _redraw_box(self):
        self._canvas.coords(
            self._rect_id,
            self._box_x1,
            self._box_y1,
            self._box_x2,
            self._box_y2,
        )
        self._canvas.coords(
            self._hori_id,
            self._box_x1,
            (self._box_y1 + self._box_y2) / 2,
            self._box_x2,
            (self._box_y1 + self._box_y2) / 2,
        )
        self._canvas.coords(
            self._vert_id,
            (self._box_x1 + self._box_x2) / 2,
            self._box_y1,
            (self._box_x1 + self._box_x2) / 2,
            self._box_y2,
        )

    def _on_click(self, event):
        self._last_x, self._last_y = event.x, event.y

    def _on_drag(self, event):
        # Move the box
        dx = event.x - self._last_x
        dy = event.y - self._last_y

        self._box_x1 += dx
        self._box_x2 += dx
        self._box_y1 += dy
        self._box_y2 += dy

        self._last_x, self._last_y = event.x, event.y
        self._redraw_box()

    def _on_click_resize(self, event):
        self._last_x, self._last_y = event.x, event.y

    def _on_drag_resize(self, event):
        # Resize by dragging (Simulates zooming)
        dy = event.y - self._last_y
        self._apply_zoom(dy)
        self._last_x, self._last_y = event.x, event.y

    def _on_scroll(self, event):
        # Handle scroll direction
        if event.num == 5 or event.delta < 0:
            self._apply_zoom(-10)  # Shrink
        else:
            self._apply_zoom(10)  # Grow

    def _apply_zoom(self, amount):
        # Calculate aspect-ratio compliant resize
        # amount > 0: Grow box (Zoom out effect)
        # amount < 0: Shrink box (Zoom in effect)
        current_w = self._box_x2 - self._box_x1

        # Limit min size
        if amount < 0 and current_w < 50:
            return

        # Maintain aspect ratio
        change_w = amount
        change_h = amount / self._aspect_ratio

        # Grow/Shrink from center
        self._box_x1 -= change_w / 2
        self._box_x2 += change_w / 2
        self._box_y1 -= change_h / 2
        self._box_y2 += change_h / 2

        self._redraw_box()

    def _on_finish(self, _):
        # Convert display coords back to original image coords
        x1 = int(self._box_x1 / self._scale)
        y1 = int(self._box_y1 / self._scale)
        x2 = int(self._box_x2 / self._scale)
        y2 = int(self._box_y2 / self._scale)
        self.final_crop_box = (x1, y1, x2, y2)
        self._root.destroy()


def create_photo_sheet(
    input_path: str,
    output_path: str,
    layout: PhotoSheetLayout = PhotoSheetLayout.ONE_INCH_TAIWAN,
):
    """
    Layouts a photo onto a 4x6 inch canvas for printing.
    Default size: Taiwan 1-inch (2.8cm x 3.5cm).
    """

    # Configuration
    dpi = 1000

    # Canvas: 4x6 inches
    canvas_w_inch = 6
    canvas_h_inch = 4
    canvas_size = (int(canvas_w_inch * dpi), int(canvas_h_inch * dpi))

    # Photo size
    photo_w_cm, photo_h_cm = layout.value
    photo_w_px = int((photo_w_cm / 2.54) * dpi)
    photo_h_px = int((photo_h_cm / 2.54) * dpi)
    photo_aspect = photo_w_px / photo_h_px

    # Layout (pixels)
    gap = 0
    border_w = 2
    border_color = "#CCCCCC"

    try:
        # Check input file existence
        if not os.path.exists(input_path):
            print(f"❌ Error: Input file '{input_path}' not found.")
            sys.exit(1)

        # Load image
        img = Image.open(input_path)

        # Create canvas
        canvas = Image.new("RGB", canvas_size, "white")

        # Expand image with white background for cropping
        img_expanded = Image.new(
            "RGB", (int(img.width * 1.5), int(img.height * 1.5)), "white"
        )
        img_expanded.paste(img, (int(img.width * 0.25), int(img.height * 0.25)))
        # Interactive cropping
        cropper = AspectCropDialog(img_expanded, photo_aspect)
        cropper.run()
        if cropper.final_crop_box:
            img_cropped = img_expanded.crop(cropper.final_crop_box)
            img_resized = img_cropped.resize(
                (photo_w_px, photo_h_px), Image.Resampling.LANCZOS
            )
        else:
            print("⚠️ Window closed without Enter. Using Center Crop.")
            img_resized = ImageOps.fit(
                img, (photo_w_px, photo_h_px), method=Image.Resampling.LANCZOS
            )

        # Add cutting border
        img_with_border = ImageOps.expand(
            img_resized, border=border_w, fill=border_color
        )
        w_final, h_final = img_with_border.size

        # Arrange on grid
        x_offset = gap
        y_offset = gap
        count = 0

        while y_offset + h_final < canvas_size[1]:
            while x_offset + w_final < canvas_size[0]:
                canvas.paste(img_with_border, (x_offset, y_offset))
                x_offset += w_final + gap
                count += 1
            x_offset = gap
            y_offset += h_final + gap

        # Save
        canvas.save(output_path, quality=100, dpi=(dpi, dpi))
        print(f"✅ Success! Saved to: {output_path}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ An error occurred: {e}")
        sys.exit(1)
