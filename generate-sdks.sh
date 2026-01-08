#!/bin/bash
set -e

# Variables
SMITHY_SERVICE="ConfigurationService"
OPENAPI_SPEC="build/smithy/source/openapi/${SMITHY_SERVICE}.openapi.json"
OUTPUT_DIR="./src/generated_sdk"
LANGUAGES=("cpp-restsdk" "python" "typescript" "cpp-tiny" "cpp-oatpp-client")

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
if [ "$LANG" = "python" ]; then
    OUTPUT_PATH="./src/generatedSDKPython"
else
    OUTPUT_PATH="$OUTPUT_DIR/$LANG"
fi

openapi-generator generate \
    -i "$OPENAPI_SPEC" \
    -g "$LANG" \
    -o "$OUTPUT_PATH" \
    --additional-properties=projectName="${SMITHY_SERVICE}SDK"

echo "✅ Done! $LANG SDK is in $OUTPUT_PATH"