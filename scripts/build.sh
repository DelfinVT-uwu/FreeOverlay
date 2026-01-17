#!/bin/bash
# Build script for FreeOverlay on Linux
# Usage: ./scripts/build.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="$PROJECT_ROOT/python"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 FreeOverlay Build Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Check PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${BLUE}📦 Installing PyInstaller...${NC}"
    python3 -m pip install PyInstaller
fi

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
python3 -m pip install -q -r "$PYTHON_DIR/requirements.txt"
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run build
echo -e "${BLUE}🔨 Building executable...${NC}"
cd "$PROJECT_ROOT"
python3 scripts/build.py

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📁 Output directory: dist/"
echo "📦 Executable: dist/FreeOverlay"
echo ""
