#!/bin/bash
set -e

# Wrapper script that calls both model generators
# Individual generators are now in their respective model directories:
#   - src/models/tr12/generate-tr12-models.sh
#   - src/models/cdd_sdk/generate-client-sdk-models.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo "🚀 Generating TR12 models..."
"$SCRIPT_DIR/src/models/tr12/generate-tr12-models.sh" "$LANG"

echo ""
echo "🚀 Generating Client SDK models..."
"$SCRIPT_DIR/src/models/cdd_sdk/generate-client-sdk-models.sh" "$LANG"

echo ""
echo "✅ All models generated!"
