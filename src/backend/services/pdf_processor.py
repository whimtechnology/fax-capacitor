"""
FaxTriage AI — PDF Processing Service

Converts PDF documents to base64-encoded images for Claude Vision API.
Ported from scripts/test_classification.py
"""
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image

# Try to import pdf2image for fallback
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def is_image_black_or_empty(img_bytes: bytes, threshold: float = 0.05) -> bool:
    """
    Check if an image is mostly black/empty by analyzing pixel values.

    Args:
        img_bytes: PNG image bytes
        threshold: Maximum average brightness (0-1) to consider "black"

    Returns:
        True if image appears black/empty
    """
    try:
        img = Image.open(BytesIO(img_bytes))
        gray = img.convert('L')
        pixels = list(gray.getdata())
        avg_brightness = sum(pixels) / (len(pixels) * 255.0)
        return avg_brightness < threshold
    except Exception:
        return False


def pdf_to_base64_images_pymupdf(
    pdf_path: str,
    pages_to_process: int,
    dpi: int = 300
) -> tuple[list[str], bool]:
    """
    Convert PDF pages using PyMuPDF.

    Returns:
        Tuple of (list of base64 images, success flag)

    Raises:
        PDFProcessingError: If PDF cannot be opened or rendered
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFProcessingError(f"Failed to open PDF: {e}")

    # Check for password-protected PDFs
    if doc.is_encrypted:
        doc.close()
        raise PDFProcessingError("PDF is password-protected and cannot be processed")

    images = []
    all_black = True

    try:
        for page_num in range(min(pages_to_process, len(doc))):
            page = doc[page_num]
            mat = fitz.Matrix(dpi/72, dpi/72)
            # Render with alpha channel and white background to handle transparency
            pix = page.get_pixmap(matrix=mat, alpha=True)

            # If the image appears black, try rendering without alpha
            img_bytes = pix.tobytes("png")
            if is_image_black_or_empty(img_bytes):
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_bytes = pix.tobytes("png")

            if not is_image_black_or_empty(img_bytes):
                all_black = False

            b64 = base64.b64encode(img_bytes).decode("utf-8")
            images.append(b64)
    except Exception as e:
        doc.close()
        raise PDFProcessingError(f"Failed to render PDF page: {e}")

    doc.close()
    return images, not all_black


def pdf_to_base64_images_pdf2image(
    pdf_path: str,
    pages_to_process: int,
    dpi: int = 300
) -> list[str]:
    """
    Convert PDF pages using pdf2image (poppler backend).

    Returns:
        List of base64-encoded PNG image strings
    """
    if not PDF2IMAGE_AVAILABLE:
        raise RuntimeError("pdf2image not installed")

    pil_images = convert_from_path(
        pdf_path,
        dpi=dpi,
        first_page=1,
        last_page=pages_to_process,
        fmt='png'
    )

    images = []
    for img in pil_images:
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        images.append(b64)

    return images


class PDFProcessingError(Exception):
    """Error during PDF processing."""
    pass


def get_page_count(pdf_path: str) -> int:
    """Get the total number of pages in a PDF."""
    try:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        raise PDFProcessingError(f"Failed to read PDF: {e}")


def pdf_to_base64_images(
    pdf_path: str,
    max_pages: Optional[int] = None
) -> tuple[list[str], int]:
    """
    Convert PDF pages to base64-encoded PNG images at 300 DPI.

    Uses PyMuPDF as primary renderer, falls back to pdf2image (poppler)
    if the rendered images appear black/empty.

    Multi-page strategy:
    - Documents ≤5 pages: send all pages
    - Documents >5 pages: send first 3 pages only

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to process (None = use default strategy)

    Returns:
        Tuple of (list of base64 images, total page count)
    """
    total_pages = get_page_count(pdf_path)

    # Multi-page strategy: For documents over 5 pages, send only first 3 pages
    if total_pages > 5:
        pages_to_process = 3
    else:
        pages_to_process = total_pages

    if max_pages is not None:
        pages_to_process = min(pages_to_process, max_pages)

    # Try PyMuPDF first at 300 DPI
    images, success = pdf_to_base64_images_pymupdf(pdf_path, pages_to_process, dpi=300)

    if success:
        return images, total_pages

    # PyMuPDF rendered black images, try pdf2image fallback
    if PDF2IMAGE_AVAILABLE:
        try:
            images = pdf_to_base64_images_pdf2image(pdf_path, pages_to_process, dpi=300)
            return images, total_pages
        except Exception:
            # Return PyMuPDF images anyway (better than nothing)
            pass

    return images, total_pages


def assess_image_quality(images: list[str]) -> str:
    """
    Assess overall image quality from base64 images.

    Returns: "good", "fair", or "poor"
    """
    if not images:
        return "poor"

    # Simple heuristic based on image data size
    # Larger images typically have more detail
    avg_size = sum(len(img) for img in images) / len(images)

    # Base64 encoded 300 DPI letter-size page is typically 500KB-2MB
    if avg_size > 500_000:
        return "good"
    elif avg_size > 100_000:
        return "fair"
    else:
        return "poor"
