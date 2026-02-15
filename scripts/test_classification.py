"""
FaxTriage AI — Phase 1 Technical Validation Script

Tests Claude Vision API classification against synthetic fax corpus.
Run this during Phase 1 to validate the classification pipeline before building the full app.

Usage:
    python test_classification.py --fax-dir data/synthetic-faxes/
    python test_classification.py --files 02_referral_response_cardiology.pdf 08_junk_marketing_fax.pdf

Requirements:
    pip install anthropic PyMuPDF Pillow python-dotenv pdf2image

    Set ANTHROPIC_CONSOLE_KEY in a .env file or as an environment variable.

    For pdf2image fallback, install poppler:
    - Windows: Download from https://github.com/osber/poppler-windows/releases
              and add bin/ to PATH
    - Mac: brew install poppler
    - Linux: apt-get install poppler-utils
"""

import os
import sys
import json
import time
import base64
import argparse
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root (two levels up from scripts/)
load_dotenv(Path(__file__).parent.parent / ".env")

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import anthropic
import fitz  # PyMuPDF
from io import BytesIO

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def check_api_key():
    """Verify API key is set (checks ANTHROPIC_API_KEY or ANTHROPIC_CONSOLE_KEY)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_CONSOLE_KEY")
    if not api_key:
        print("ERROR: No Anthropic API key found.")
        print("\nSet ANTHROPIC_API_KEY as an environment variable:")
        print("  Windows (cmd):    set ANTHROPIC_API_KEY=sk-ant-...")
        print("  Windows (PS):     $env:ANTHROPIC_API_KEY='sk-ant-...'")
        print("  Linux/Mac:        export ANTHROPIC_API_KEY=sk-ant-...")
        print("\nOr create a .env file in the project root with:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    # Ensure ANTHROPIC_API_KEY is set for the anthropic client library
    os.environ["ANTHROPIC_API_KEY"] = api_key
    return api_key


CLASSIFICATION_PROMPT = """You are a medical document classification system for Whispering Pines Family Medicine (fax: 555-867-5309, provider: Dr. Evelyn Sato, DO). You analyze fax documents received as images and return structured classification data.

## Task
Analyze the provided fax document image(s) and:
1. Classify the document type
2. Extract key metadata fields
3. Assess priority level
4. Provide a confidence score for your classification

## Document Types
Classify into exactly ONE of the following types:
- lab_result: Blood work, pathology, imaging reports, urinalysis results
- referral_response: Specialist consultation notes, referral acknowledgments, appointment confirmations, consult reports sent back to the referring provider
- prior_auth_decision: Insurance approval, denial, or pending notices for procedures/medications/referrals
- pharmacy_request: Refill requests, formulary changes, prior auth for medications, drug interaction alerts
- insurance_correspondence: EOBs, coverage changes, claim correspondence, eligibility updates, coordination of benefits requests
- records_request: Medical records requests from other providers, attorneys, insurance companies, or patients
- marketing_junk: Vendor solicitations, equipment sales, supply catalogs, unsolicited advertisements, EHR sales pitches
- other: Anything not clearly matching the above categories, including: orphan cover pages without attached content, misdirected faxes intended for a different recipient, multi-type document bundles that don't fit a single category, or documents too illegible to classify

## Priority Levels
- critical: Critical lab values, prior auth denials near appeal deadline, STAT results
- high: Lab results with abnormal values, prior auth decisions (especially denials)
- medium: Referral responses, pharmacy requests, records requests
- low: Insurance correspondence, routine items, informational documents
- none: Marketing/junk

## Urgency Indicators
Flag any of the following if present: "CRITICAL VALUE", "STAT", "URGENT", "DENIED", "APPEAL DEADLINE", "ABNORMAL", "PANIC VALUE", specific deadline dates, "time-sensitive"

## Misdirected Fax Detection
If the document is clearly addressed to a different provider/practice (not Whispering Pines Family Medicine or Dr. Sato), flag it as possibly misdirected. This includes documents where the TO: line names a different practice or the content is clearly intended for another provider. A document CAN be relevant to our practice even if sent FROM another provider — what matters is whether it's intended FOR us.

## Output Format
Respond with ONLY a JSON object (no markdown, no explanation, no code fences):

{
  "document_type": "string (one of the types listed above)",
  "confidence": number (0.0 to 1.0),
  "priority": "string (critical/high/medium/low/none)",
  "extracted_fields": {
    "patient_name": "string or null",
    "patient_dob": "string (YYYY-MM-DD) or null",
    "sending_provider": "string or null",
    "sending_facility": "string or null",
    "document_date": "string (YYYY-MM-DD) or null",
    "fax_origin_number": "string or null",
    "urgency_indicators": ["array of strings"] or [],
    "key_details": "string - brief summary of the document's key content"
  },
  "is_continuation": false,
  "page_count_processed": number,
  "page_quality": "string (good/fair/poor)",
  "flags": ["array of any notable issues — include 'possibly_misdirected' if applicable, 'incomplete_document' if pages appear missing, 'multi_document_bundle' if fax contains multiple distinct document types"]
}

## Rules
- If you cannot determine a field, set it to null — do not guess
- If confidence is below 0.65, set document_type to "other" regardless of your best guess
- For marketing/junk, you do not need to extract patient fields
- If the document appears to be a cover sheet followed by content, classify based on the content type described in the cover sheet
- If the document is ONLY a cover sheet with no attached content, classify as "other" and flag as "incomplete_document"
- Be conservative with critical/high priority — only assign when urgency indicators are clearly present
- If multiple pages are provided, base classification on the overall document, not individual pages"""


# Expected results for validation
EXPECTED_CLASSIFICATIONS = {
    "01_lab_result_cbc.pdf": "lab_result",
    "02_referral_response_cardiology.pdf": "referral_response",
    "03_prior_auth_approved.pdf": "prior_auth_decision",
    "04_prior_auth_denied.pdf": "prior_auth_decision",
    "05_pharmacy_refill_request.pdf": "pharmacy_request",
    "06_insurance_correspondence.pdf": "insurance_correspondence",
    "07_patient_records_request.pdf": "records_request",
    "08_junk_marketing_fax.pdf": "marketing_junk",
    "09_orphan_cover_page.pdf": "referral_response",       # Classifies by described content + incomplete_document flag
    "10_chart_dump_40pages.pdf": "records_request",         # Hospital records transmission — records_request is correct
    "11_illegible_physician_notes.pdf": "referral_response",  # Physician consult notes, despite handwritten style
    "12_wrong_provider_misdirected.pdf": "prior_auth_decision",  # Correct content classification + possibly_misdirected flag
}


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
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        # Convert to grayscale
        gray = img.convert('L')
        # Get pixel data and compute average
        pixels = list(gray.getdata())
        avg_brightness = sum(pixels) / (len(pixels) * 255.0)
        return avg_brightness < threshold
    except Exception:
        return False


def pdf_to_base64_images_pymupdf(pdf_path: str, pages_to_process: int, dpi: int = 300) -> tuple[list[str], bool]:
    """
    Convert PDF pages using PyMuPDF.

    Returns:
        Tuple of (list of base64 images, success flag)
    """
    doc = fitz.open(pdf_path)
    images = []
    all_black = True

    for page_num in range(min(pages_to_process, len(doc))):
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72, dpi/72)
        # Render with alpha channel and white background to handle transparency
        pix = page.get_pixmap(matrix=mat, alpha=True)

        # If the image appears black, try rendering without alpha (force opaque)
        img_bytes = pix.tobytes("png")
        if is_image_black_or_empty(img_bytes):
            # Try again with explicit white background, no alpha
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")

        if not is_image_black_or_empty(img_bytes):
            all_black = False

        b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(b64)

    doc.close()
    return images, not all_black


def pdf_to_base64_images_pdf2image(pdf_path: str, pages_to_process: int, dpi: int = 300) -> list[str]:
    """
    Convert PDF pages using pdf2image (poppler backend).

    Returns:
        List of base64-encoded PNG image strings
    """
    if not PDF2IMAGE_AVAILABLE:
        raise RuntimeError("pdf2image not installed. Run: pip install pdf2image")

    # Convert PDF to PIL images
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


def pdf_to_base64_images(pdf_path: str, max_pages: int = None) -> list[str]:
    """
    Convert PDF pages to base64-encoded PNG images at 300 DPI.
    Uses PyMuPDF as primary renderer, falls back to pdf2image (poppler) if
    the rendered images appear black/empty.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to process (None = all pages)

    Returns:
        List of base64-encoded PNG image strings
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

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
        except Exception as e:
            print(f"    Warning: pdf2image fallback failed: {e}")
            # Return PyMuPDF images anyway (better than nothing)
    else:
        print(f"    Warning: PyMuPDF rendered black image, pdf2image not available for fallback")

    return images, total_pages


def classify_document(images: list[str], page_count: int) -> dict:
    """
    Send document images to Claude Vision API for classification.

    Args:
        images: List of base64-encoded PNG image strings
        page_count: Total number of pages in the document

    Returns:
        Parsed JSON classification result
    """
    client = anthropic.Anthropic()

    # Build content with all images
    content = []
    for i, img in enumerate(images):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img
            }
        })

    # Add instruction text
    pages_note = f"(showing {len(images)} of {page_count} pages)" if len(images) < page_count else f"({len(images)} pages)"
    content.append({
        "type": "text",
        "text": f"Classify this fax document {pages_note}."
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        system=CLASSIFICATION_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    # Parse the JSON response
    response_text = response.content[0].text.strip()

    # Handle potential markdown code fences (shouldn't happen with good prompt, but defensive)
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (code fences)
        response_text = "\n".join(lines[1:-1])

    result = json.loads(response_text)

    # Add API usage info for cost tracking
    result["_api_usage"] = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return result


def validate_json_structure(result: dict) -> list[str]:
    """Validate the classification response has required fields."""
    errors = []
    required_fields = ["document_type", "confidence", "priority", "extracted_fields"]
    for field in required_fields:
        if field not in result:
            errors.append(f"Missing required field: {field}")

    valid_types = [
        "lab_result", "referral_response", "prior_auth_decision",
        "pharmacy_request", "insurance_correspondence", "records_request",
        "marketing_junk", "other"
    ]
    if result.get("document_type") not in valid_types:
        errors.append(f"Invalid document_type: {result.get('document_type')}")

    valid_priorities = ["critical", "high", "medium", "low", "none"]
    if result.get("priority") not in valid_priorities:
        errors.append(f"Invalid priority: {result.get('priority')}")

    confidence = result.get("confidence", -1)
    if not (0.0 <= confidence <= 1.0):
        errors.append(f"Confidence out of range: {confidence}")

    return errors


def run_validation(fax_dir: str, specific_files: list[str] = None):
    """Run classification validation against PDFs in directory.

    Args:
        fax_dir: Directory containing synthetic fax PDFs
        specific_files: If provided, only test these specific files (names only)
    """
    # Verify API key is available before processing
    check_api_key()

    fax_path = Path(fax_dir)
    if not fax_path.exists():
        print(f"Error: Directory {fax_dir} not found")
        print("Create synthetic fax PDFs first (see docs/PROJECT_PLAN.md Step 1)")
        sys.exit(1)

    pdf_files = sorted(fax_path.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {fax_dir}")
        sys.exit(1)

    # Filter to specific files if requested
    if specific_files:
        pdf_files = [f for f in pdf_files if f.name in specific_files]
        if not pdf_files:
            print(f"None of the specified files found: {specific_files}")
            sys.exit(1)

    print(f"\nFaxTriage AI — Phase 1 Validation")
    print(f"{'=' * 70}")
    print(f"Found {len(pdf_files)} PDF files to test\n")

    results = []
    total_input_tokens = 0
    total_output_tokens = 0

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}...")
        start_time = time.time()

        try:
            images, page_count = pdf_to_base64_images(str(pdf_file))
            classification = classify_document(images, page_count)
            elapsed = (time.time() - start_time) * 1000

            # Track token usage
            api_usage = classification.pop("_api_usage", {})
            total_input_tokens += api_usage.get("input_tokens", 0)
            total_output_tokens += api_usage.get("output_tokens", 0)

            # Validate structure
            errors = validate_json_structure(classification)

            # Check against expected (if defined)
            expected = EXPECTED_CLASSIFICATIONS.get(pdf_file.name)
            correct = classification.get("document_type") == expected if expected else None

            # Get flags for display
            flags = classification.get("flags", [])

            result = {
                "file": pdf_file.name,
                "classified_as": classification.get("document_type"),
                "confidence": classification.get("confidence"),
                "priority": classification.get("priority"),
                "expected": expected,
                "correct": correct,
                "errors": errors,
                "time_ms": round(elapsed),
                "pages_total": page_count,
                "pages_processed": len(images),
                "flags": flags,
                "full_response": classification,
            }
            results.append(result)

            status = "✓" if correct else ("✗" if correct is False else "?")
            print(f"  {status} Type: {result['classified_as']} "
                  f"(conf: {result['confidence']:.2f}, "
                  f"pri: {result['priority']}, "
                  f"{result['time_ms']}ms)")
            if flags:
                print(f"    Flags: {', '.join(flags)}")
            if errors:
                for e in errors:
                    print(f"  ⚠ {e}")

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON Parse Error: {e}")
            results.append({"file": pdf_file.name, "error": f"JSON Parse Error: {e}"})
        except anthropic.APIError as e:
            print(f"  ✗ API Error: {e}")
            results.append({"file": pdf_file.name, "error": f"API Error: {e}"})
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({"file": pdf_file.name, "error": str(e)})

    # Summary Table
    print(f"\n{'=' * 70}")
    print("RESULTS TABLE")
    print(f"{'=' * 70}")
    print(f"{'Filename':<40} {'Expected':<20} {'Actual':<20} {'Match':<6} {'Conf':<6} {'Pri':<8} {'Time':<8} {'Flags'}")
    print(f"{'-' * 40} {'-' * 20} {'-' * 20} {'-' * 6} {'-' * 6} {'-' * 8} {'-' * 8} {'-' * 20}")

    for r in results:
        if "error" in r and "classified_as" not in r:
            print(f"{r['file']:<40} {'ERROR':<20} {r.get('error', 'Unknown')[:50]}")
            continue

        match = "Y" if r.get("correct") else ("N" if r.get("correct") is False else "?")
        flags_str = ", ".join(r.get("flags", []))[:30] if r.get("flags") else ""
        print(f"{r['file']:<40} {r.get('expected', 'N/A'):<20} {r.get('classified_as', 'N/A'):<20} {match:<6} {r.get('confidence', 0):.2f}   {r.get('priority', 'N/A'):<8} {r.get('time_ms', 0):<8} {flags_str}")

    # Summary Statistics
    print(f"\n{'=' * 70}")
    print("SUMMARY STATISTICS")
    print(f"{'=' * 70}")

    tested = [r for r in results if "classified_as" in r]
    if tested:
        with_expected = [r for r in tested if r["correct"] is not None]
        if with_expected:
            correct_count = sum(1 for r in with_expected if r["correct"])
            print(f"Accuracy: {correct_count}/{len(with_expected)} ({correct_count/len(with_expected)*100:.0f}%)")

        avg_confidence = sum(r["confidence"] for r in tested) / len(tested)
        avg_time = sum(r["time_ms"] for r in tested) / len(tested)
        print(f"Avg confidence: {avg_confidence:.2f}")
        print(f"Avg processing time: {avg_time:.0f}ms")

        # Token usage and cost estimate
        print(f"\nAPI Usage:")
        print(f"  Total input tokens: {total_input_tokens:,}")
        print(f"  Total output tokens: {total_output_tokens:,}")
        # Claude Sonnet pricing (approximate): $3/1M input, $15/1M output
        input_cost = (total_input_tokens / 1_000_000) * 3.0
        output_cost = (total_output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost
        print(f"  Estimated cost: ${total_cost:.4f}")

        # Classification distribution
        print(f"\nClassification Distribution:")
        type_counts = {}
        for r in tested:
            t = r["classified_as"]
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in sorted(type_counts.items()):
            print(f"  {t}: {count}")

        # Misclassifications detail
        misclassified = [r for r in with_expected if not r["correct"]]
        if misclassified:
            print(f"\nMisclassifications ({len(misclassified)}):")
            for r in misclassified:
                print(f"  {r['file']}: expected '{r['expected']}', got '{r['classified_as']}' (conf: {r['confidence']:.2f})")
                key_details = r.get("full_response", {}).get("extracted_fields", {}).get("key_details", "")
                if key_details:
                    print(f"    Details: {key_details[:100]}...")

    # Save detailed results
    output_file = "phase1_validation_results.json"
    output_data = {
        "run_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": len(pdf_files),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "results": results,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FaxTriage AI Phase 1 Validation")
    parser.add_argument("--fax-dir", default="data/synthetic-faxes/",
                        help="Directory containing synthetic fax PDFs")
    parser.add_argument("--files", nargs="+",
                        help="Specific PDF files to test (names only, not paths)")
    args = parser.parse_args()
    run_validation(args.fax_dir, specific_files=args.files)
