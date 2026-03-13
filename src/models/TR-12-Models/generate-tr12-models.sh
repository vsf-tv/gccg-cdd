#!/bin/bash
set -e

# Generates TR12 protocol models (HostServiceApi)
# Run this script from src/models/tr12 directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INTERNAL_SERVICE="HostServiceApi"
INTERNAL_SPEC="build/smithy/source/openapi/${INTERNAL_SERVICE}.openapi.json"
OUTPUT_DIR="./generated/tr12"
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

# 1. Build the Smithy TR12 models
echo "🚀 Building Smithy TR12 model..."
smithy build

# 2. Check for spec
if [ ! -f "$INTERNAL_SPEC" ]; then
    echo "❌ Error: TR12 OpenAPI spec not found at $INTERNAL_SPEC"
    exit 1
fi

# 3. Generate TR12 models
OUTPUT_PATH="${OUTPUT_DIR}${LANG}"
echo "📦 Generating TR12 models..."
if [ "$LANG" = "python" ]; then
    openapi-generator generate \
        -i "$INTERNAL_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${INTERNAL_SERVICE}SDK",packageName=tr12_api_client
else
    openapi-generator generate \
        -i "$INTERNAL_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${INTERNAL_SERVICE}SDK"
fi

echo "✅ Done! TR12 SDK is in $OUTPUT_PATH"
