"""
FaxTriage AI — Phase 1 Technical Validation Script

Tests Claude Vision API classification against synthetic fax corpus.
Run this during Phase 1 to validate the classification pipeline before building the full app.

Usage:
    python test_classification.py --fax-dir data/synthetic-faxes/

Requirements:
    pip install anthropic PyMuPDF Pillow
    
    Set ANTHROPIC_API_KEY environment variable.
"""

import os
import sys
import json
import time
import base64
import argparse
from pathlib import Path

# Placeholder — install anthropic SDK before running
# import anthropic
# import fitz  # PyMuPDF


CLASSIFICATION_PROMPT = """
You are a medical document classification system for a small healthcare practice.
[Full prompt from prompts/CLASSIFICATION_PROMPT.md — paste here during Phase 1]
"""

# Expected results for validation (fill in after creating synthetic corpus)
EXPECTED_CLASSIFICATIONS = {
    # "lab_result_sample.pdf": "lab_result",
    # "referral_response_sample.pdf": "referral_response",
    # "prior_auth_denial_sample.pdf": "prior_auth_decision",
    # "pharmacy_refill_sample.pdf": "pharmacy_request",
    # "insurance_eob_sample.pdf": "insurance_correspondence",
    # "records_request_sample.pdf": "records_request",
    # "marketing_junk_sample.pdf": "marketing_junk",
}


def pdf_to_base64_images(pdf_path: str) -> list[str]:
    """Convert PDF pages to base64-encoded PNG images."""
    # TODO: Implement with PyMuPDF during Phase 1
    # import fitz
    # doc = fitz.open(pdf_path)
    # images = []
    # for page in doc:
    #     pix = page.get_pixmap(dpi=200)
    #     img_bytes = pix.tobytes("png")
    #     b64 = base64.b64encode(img_bytes).decode("utf-8")
    #     images.append(b64)
    # return images
    raise NotImplementedError("Implement during Phase 1 build")


def classify_document(images: list[str]) -> dict:
    """Send document images to Claude Vision API for classification."""
    # TODO: Implement with Anthropic SDK during Phase 1
    # client = anthropic.Anthropic()
    # content = []
    # for img in images:
    #     content.append({
    #         "type": "image",
    #         "source": {"type": "base64", "media_type": "image/png", "data": img}
    #     })
    # content.append({"type": "text", "text": "Classify this fax document."})
    #
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=1024,
    #     temperature=0,
    #     system=CLASSIFICATION_PROMPT,
    #     messages=[{"role": "user", "content": content}]
    # )
    # return json.loads(response.content[0].text)
    raise NotImplementedError("Implement during Phase 1 build")


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


def run_validation(fax_dir: str):
    """Run classification validation against all PDFs in directory."""
    fax_path = Path(fax_dir)
    if not fax_path.exists():
        print(f"Error: Directory {fax_dir} not found")
        print("Create synthetic fax PDFs first (see docs/PROJECT_PLAN.md Step 1)")
        sys.exit(1)

    pdf_files = sorted(fax_path.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {fax_dir}")
        sys.exit(1)

    print(f"\nFaxTriage AI — Phase 1 Validation")
    print(f"{'=' * 50}")
    print(f"Found {len(pdf_files)} PDF files to test\n")

    results = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}...")
        start_time = time.time()

        try:
            images = pdf_to_base64_images(str(pdf_file))
            classification = classify_document(images)
            elapsed = (time.time() - start_time) * 1000

            # Validate structure
            errors = validate_json_structure(classification)

            # Check against expected (if defined)
            expected = EXPECTED_CLASSIFICATIONS.get(pdf_file.name)
            correct = classification.get("document_type") == expected if expected else None

            result = {
                "file": pdf_file.name,
                "classified_as": classification.get("document_type"),
                "confidence": classification.get("confidence"),
                "priority": classification.get("priority"),
                "expected": expected,
                "correct": correct,
                "errors": errors,
                "time_ms": round(elapsed),
                "full_response": classification,
            }
            results.append(result)

            status = "✓" if correct else ("✗" if correct is False else "?")
            print(f"  {status} Type: {result['classified_as']} "
                  f"(confidence: {result['confidence']:.2f}, "
                  f"priority: {result['priority']}, "
                  f"{result['time_ms']}ms)")
            if errors:
                for e in errors:
                    print(f"  ⚠ {e}")

        except NotImplementedError:
            print("  ⚠ Classification not yet implemented — complete Phase 1 setup first")
            break
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({"file": pdf_file.name, "error": str(e)})

    # Summary
    if results and "error" not in results[0]:
        print(f"\n{'=' * 50}")
        print("SUMMARY")
        tested = [r for r in results if "correct" in r]
        if tested:
            with_expected = [r for r in tested if r["correct"] is not None]
            if with_expected:
                correct_count = sum(1 for r in with_expected if r["correct"])
                print(f"Accuracy: {correct_count}/{len(with_expected)} "
                      f"({correct_count/len(with_expected)*100:.0f}%)")
            avg_confidence = sum(r["confidence"] for r in tested) / len(tested)
            avg_time = sum(r["time_ms"] for r in tested) / len(tested)
            print(f"Avg confidence: {avg_confidence:.2f}")
            print(f"Avg processing time: {avg_time:.0f}ms")

    # Save detailed results
    output_file = "phase1_validation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FaxTriage AI Phase 1 Validation")
    parser.add_argument("--fax-dir", default="data/synthetic-faxes/",
                        help="Directory containing synthetic fax PDFs")
    args = parser.parse_args()
    run_validation(args.fax_dir)
