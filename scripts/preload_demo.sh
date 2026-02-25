#!/usr/bin/env bash
#
# preload_demo.sh - Batch upload synthetic faxes to Fax Capacitor
#
# Usage:
#   ./scripts/preload_demo.sh [BASE_URL]
#
# Arguments:
#   BASE_URL  Target server URL (default: https://faxcapacitor.xyz)
#
# Examples:
#   ./scripts/preload_demo.sh                           # Upload to live site
#   ./scripts/preload_demo.sh http://localhost:8000     # Upload to local dev
#
# Notes:
#   - Uploads all synthetic PDFs from data/synthetic-faxes/
#   - Each upload triggers AI classification (Claude API call)
#   - 2-second delay between uploads to avoid overwhelming the classifier
#   - Continues on errors and reports summary at end
#

set -euo pipefail

BASE_URL="${1:-https://faxcapacitor.xyz}"
FAXES_DIR="data/synthetic-faxes"
UPLOAD_ENDPOINT="$BASE_URL/api/documents/upload"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "Fax Capacitor Demo Pre-Load Script"
echo "============================================"
echo "Target: $BASE_URL"
echo ""

# Check if faxes directory exists
if [[ ! -d "$FAXES_DIR" ]]; then
    echo -e "${RED}Error: Directory '$FAXES_DIR' not found${NC}"
    echo "Run this script from the project root directory."
    exit 1
fi

# Count PDFs
pdf_files=("$FAXES_DIR"/*.pdf)
total=${#pdf_files[@]}

if [[ $total -eq 0 ]]; then
    echo -e "${RED}Error: No PDF files found in '$FAXES_DIR'${NC}"
    exit 1
fi

echo "Found $total PDF files to upload"
echo ""

success=0
failed=0

for pdf in "${pdf_files[@]}"; do
    filename=$(basename "$pdf")

    # Upload and capture HTTP status code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -F "files=@$pdf" \
        "$UPLOAD_ENDPOINT" 2>/dev/null) || http_code="000"

    if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
        echo -e "${GREEN}[PASS]${NC} $filename (HTTP $http_code)"
        ((++success))
    else
        echo -e "${RED}[FAIL]${NC} $filename (HTTP $http_code)"
        ((++failed))
    fi

    # Delay between uploads (skip after last file)
    if [[ "$pdf" != "${pdf_files[-1]}" ]]; then
        sleep 2
    fi
done

echo ""
echo "============================================"
echo "Summary"
echo "============================================"

if [[ $failed -eq 0 ]]; then
    echo -e "${GREEN}$success of $total uploaded successfully${NC}"
else
    echo -e "${YELLOW}$success of $total uploaded successfully${NC}"
    echo -e "${RED}$failed failed${NC}"
fi

exit $failed
