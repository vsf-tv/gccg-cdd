#!/bin/bash
set -e

# Generates CDD Client SDK models (CddService)
# Run this script from src/models/cdd_sdk directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SMITHY_SERVICE="CddService"
OPENAPI_SPEC="build/smithy/source/openapi/${SMITHY_SERVICE}.openapi.json"
OUTPUT_DIR="./generated/cdd_sdk"
LANGUAGES=("cpp-restsdk" "python" "typescript" "cpp-tiny" "cpp-oatpp-client" "golang")

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <language>"
    echo "Supported languages: ${LANGUAGES[*]}"
    exit 1
fi

LANG="$1"

# Validate language
if [[ ! " ${LANGUAGES[*]} " =~ " ${LANG} " ]]; then
    echo "❌ Error: Unsupported language '$LANG'"
    echo "Supported languages: ${LANGUAGES[*]}"
    exit 1
fi

# 1. Build the Smithy SDK model
echo "🚀 Building Smithy Client SDK model..."
smithy build

# 2. Check for spec
if [ ! -f "$OPENAPI_SPEC" ]; then
    echo "❌ Error: OpenAPI spec not found at $OPENAPI_SPEC"
    exit 1
fi

# 3. Generate SDK models
OUTPUT_PATH="${OUTPUT_DIR}${LANG}"
echo "📦 Generating Client SDK models..."
if [ "$LANG" = "python" ]; then
    openapi-generator generate \
        -i "$OPENAPI_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${SMITHY_SERVICE}SDK",packageName=cdd_sdk_client
else
    openapi-generator generate \
        -i "$OPENAPI_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${SMITHY_SERVICE}SDK"
fi

echo "✅ Done! Client SDK is in $OUTPUT_PATH"
