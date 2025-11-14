import argparse
import os

from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

def pdf_to_image(pdf_path, dpi=200):
    """
    Convert the first page of a PDF to a PIL image.
    """
    pages = convert_from_path(pdf_path, dpi=dpi)
    return pages[0]


def detect_highlight_boxes(template_img):
    """
    Detect highlighted regions on a template image.

    Uses simple HSV color thresholding to find yellow highlights.
    Adjust the HSV values if your highlights are a different color.
    """
    # Convert PIL image to OpenCV BGR
    template_cv = cv2.cvtColor(np.array(template_img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(template_cv, cv2.COLOR_BGR2HSV)

    # Yellow highlight color range (tunable)
    lower_yellow = np.array([20, 50, 150])
    upper_yellow = np.array([40, 255, 255])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Reduce noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    # Find highlight regions
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 200:  # filter tiny noise
            boxes.append((x, y, w, h))

    # Return boxes and template image size
    return boxes, template_cv.shape[1], template_cv.shape[0]


def draw_boxes_on_image(target_img, boxes, template_size, color=(255, 255, 0), alpha=0.35):
    """
    Draw semi-transparent rectangles on the target image using the
    highlight coordinates from the template.
    """
    target_cv = cv2.cvtColor(np.array(target_img), cv2.COLOR_RGB2BGR)

    template_w, template_h = template_size
    target_h, target_w = target_cv.shape[:2]

    # Scale boxes if the target PDF size differs from the template
    scale_x = target_w / template_w
    scale_y = target_h / template_h

    overlay = target_cv.copy()

    for (x, y, w, h) in boxes:
        x1 = int(x * scale_x)
        y1 = int(y * scale_y)
        x2 = int((x + w) * scale_x)
        y2 = int((y + h) * scale_y)

        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

    cv2.addWeighted(overlay, alpha, target_cv, 1 - alpha, 0, target_cv)

    return Image.fromarray(cv2.cvtColor(target_cv, cv2.COLOR_BGR2RGB))


def images_to_pdf(images, output_pdf_path):
    """
    Save one or more PIL images as a new PDF.
    """
    if not images:
        raise ValueError("No images to save.")

    images[0].save(
        output_pdf_path,
        "PDF",
        resolution=200.0,
        save_all=True,
        append_images=images[1:]
    )


def main(template_path, input_path, output_path):
    # Load pages
    template_img = pdf_to_image(template_path)
    input_img = pdf_to_image(input_path)

    # Extract highlight regions
    boxes, template_w, template_h = detect_highlight_boxes(template_img)

    if not boxes:
        print("No highlight regions detected on template PDF.")
        return

    # Apply boxes to input PDF
    result_img = draw_boxes_on_image(
        input_img,
        boxes,
        template_size=(template_w, template_h)
    )

    # Save final PDF
    images_to_pdf([result_img], output_path)

    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clone highlight regions from a template PDF onto another PDF.")
    parser.add_argument("--template", required=True, help="Path to the highlighted template PDF.")
    parser.add_argument("--input", required=True, help="Path to the input PDF.")
    parser.add_argument("--output", required=True, help="Path to save the output PDF.")

    args = parser.parse_args()

    if not os.path.exists(args.template):
        raise FileNotFoundError(f"Template PDF not found: {args.template}")
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input PDF not found: {args.input}")

    main(args.template, args.input, args.output)
