#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path-to-protos-dir>"
    exit 1
fi

OUT_DIR=protos

mkdir -p "${OUT_DIR}"

EXEC=pyenv exec

# check if pyenv is installed
if ! command -v "${EXEC}" &> /dev/null
then
    EXEC=""
fi

${EXEC} pip install grpcio-tools

${EXEC} python -m grpc_tools.protoc \
    -I "$1" \
    --python_out="${OUT_DIR}" \
    --grpc_python_out="${OUT_DIR}" \
    "$1"/*.proto
