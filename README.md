# PDF Highlight Cloner

Manually highlighting the same sections across dozens of PDFs is a huge time sink.

This project is a Python tool that:
- Takes a **template PDF** where the relevant text is already highlighted
- Detects those highlight regions
- Aligns a **new PDF** to that template
- Automatically applies the same highlight zones to the new document
- Exports the result as a new, annotated PDF

I built this using **public PDFs from Google only** — no proprietary or client data.

---

## How it works (high-level)

1. Convert the template and target PDFs into images using `pdf2image`.
2. Detect highlight regions on the template page using OpenCV (by color thresholding).
3. Optionally align/resize the target page to match the template.
4. Draw the same highlight boxes onto the target document.
5. Save the result as a new PDF.

The goal is to turn a repetitive, manual review process into something that runs in **seconds**.

---

## Project structure

```text
pdf-highlight-cloner/
│
├─ README.md               # This file
├─ requirements.txt        # Python dependencies
├─ clone_highlights.py     # Main script
└─ sample_pdfs/
   ├─ template_example.pdf            # Highlighted template document
   └─ demo_input.pdf                  # Un-highlighted document

### Usage

Run the script from the command line:

```bash
python clone_highlights.py \
  --template sample_pdfs/template_example.pdf \
  --input sample_pdfs/demo_input.pdf \
  --output sample_pdfs/demo_output.pdf

