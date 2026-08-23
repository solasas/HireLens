"""Builds small, real PDFs in memory for exercising app.services.pdf_parser.

Using PyMuPDF to build the fixtures (rather than checking in binary .pdf
files) keeps the test suite self-contained and makes every fixture's
content explicit in the test that uses it.
"""

import pymupdf


def make_text_pdf(pages: list[str]) -> bytes:
    """A PDF with one page of body text per entry in `pages`."""
    document = pymupdf.open()
    try:
        for page_text in pages:
            page = document.new_page()
            y = 72
            for line in page_text.splitlines():
                page.insert_text((72, y), line)
                y += 18
        return document.tobytes()
    finally:
        document.close()


def make_blank_pdf(page_count: int = 1) -> bytes:
    """A structurally valid PDF whose pages carry no text or images."""
    document = pymupdf.open()
    try:
        for _ in range(page_count):
            document.new_page()
        return document.tobytes()
    finally:
        document.close()


def make_image_only_pdf() -> bytes:
    """A single-page PDF containing a raster image and no text layer —
    stands in for a scanned resume."""
    document = pymupdf.open()
    try:
        page = document.new_page()
        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 200))
        pixmap.clear_with(200)
        page.insert_image(pymupdf.Rect(50, 50, 250, 250), pixmap=pixmap)
        return document.tobytes()
    finally:
        document.close()
