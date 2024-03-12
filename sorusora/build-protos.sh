#!/bin/bash

PROTO_DIR=../protos
OUT_DIR=protos

mkdir -p "${OUT_DIR}"

EXEC=pyenv exec

# check if pyenv is installed
if ! command -v "${EXEC}" &> /dev/null
then
    EXEC=""
fi

${EXEC} pip install -r requirements.txt

${EXEC} python -m grpc_tools.protoc \
    -I "${PROTO_DIR}" \
    --python_out="${OUT_DIR}" \
    --grpc_python_out="${OUT_DIR}" \
    "${PROTO_DIR}"/*.proto
