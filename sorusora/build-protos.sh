#!/bin/bash

if [[ $# -eq 1 ]]; then
    PROTO_DIR=$1
else
    PROTO_DIR=../protos
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
    -I "${PROTO_DIR}" \
    --python_out="${OUT_DIR}" \
    --grpc_python_out="${OUT_DIR}" \
    "${PROTO_DIR}"/*.proto
