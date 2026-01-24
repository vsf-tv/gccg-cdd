#!/bin/bash
set -e

# Variables
SMITHY_SERVICE="CddService"
INTERNAL_SERVICE="HostServiceApi"
OPENAPI_SPEC="build/smithy/source/openapi/${SMITHY_SERVICE}.openapi.json"
INTERNAL_SPEC="build/smithy/source/openapi/${INTERNAL_SERVICE}.openapi.json"
OUTPUT_DIR="./src/generatedSDK"
INTERNAL_OUTPUT_DIR="./src/generatedSDKInternal"
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

# 1. Build the Smithy models
echo "🚀 Building Smithy SDK model..."
smithy build

echo "🚀 Building Smithy Internal model..."
smithy build --config smithy-build-internal.json

# 2. Check for specs
if [ ! -f "$OPENAPI_SPEC" ]; then
    echo "❌ Error: OpenAPI spec not found at $OPENAPI_SPEC"
    exit 1
fi

if [ ! -f "$INTERNAL_SPEC" ]; then
    echo "❌ Error: Internal OpenAPI spec not found at $INTERNAL_SPEC"
    exit 1
fi

# 3. Generate SDK models
OUTPUT_PATH="$OUTPUT_DIR$LANG"
echo "📦 Generating SDK models..."
if [ "$LANG" = "python" ]; then
    openapi-generator generate \
        -i "$OPENAPI_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${SMITHY_SERVICE}SDK",packageName=openapi_client
else
    openapi-generator generate \
        -i "$OPENAPI_SPEC" \
        -g "$LANG" \
        -o "$OUTPUT_PATH" \
        --additional-properties=projectName="${SMITHY_SERVICE}SDK"
fi

# 4. Generate Internal models
INTERNAL_OUTPUT_PATH="$INTERNAL_OUTPUT_DIR$LANG"
echo "📦 Generating Internal models..."
if [ "$LANG" = "python" ]; then
    openapi-generator generate \
        -i "$INTERNAL_SPEC" \
        -g "$LANG" \
        -o "$INTERNAL_OUTPUT_PATH" \
        --additional-properties=projectName="${INTERNAL_SERVICE}SDK",packageName=internal_api_client
else
    openapi-generator generate \
        -i "$INTERNAL_SPEC" \
        -g "$LANG" \
        -o "$INTERNAL_OUTPUT_PATH" \
        --additional-properties=projectName="${INTERNAL_SERVICE}SDK"
fi

echo "✅ Done! SDK is in $OUTPUT_PATH"
echo "✅ Done! Internal SDK is in $INTERNAL_OUTPUT_PATH"