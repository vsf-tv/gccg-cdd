#!/bin/bash
set -e

# Variables
SMITHY_SERVICE="ConfigurationService"
OPENAPI_SPEC="build/smithy/source/openapi/${SMITHY_SERVICE}.openapi.json"
OUTPUT_DIR="./generated-sdk"
LANGUAGES=("cpp-restsdk" "python" "typescript")

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

# 1. Build the Smithy model
echo "🚀 Building Smithy model..."
smithy build

# 2. Check for spec
if [ ! -f "$OPENAPI_SPEC" ]; then
    echo "❌ Error: OpenAPI spec not found at $OPENAPI_SPEC"
    exit 1
fi

# 3. Generate SDK
echo "🛠️  Generating $LANG SDK..."
openapi-generator generate \
    -i "$OPENAPI_SPEC" \
    -g "$LANG" \
    -o "$OUTPUT_DIR/$LANG" \
    --additional-properties=projectName="${SMITHY_SERVICE}SDK"

echo "✅ Done! $LANG SDK is in $OUTPUT_DIR/$LANG"