#!/bin/bash
# Source this file before running the SDK: source setup_env.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src:${SCRIPT_DIR}/src/generatedSDKpython:${SCRIPT_DIR}/src/generatedSDKInternalpython:${PYTHONPATH}"
export PYTHONPATH=".:${SCRIPT_DIR}/src:${SCRIPT_DIR}/src/generatedSDKpython:${SCRIPT_DIR}/src/generatedSDKInternalpython:${PYTHONPATH}"
echo "PYTHONPATH set to: $PYTHONPATH"
