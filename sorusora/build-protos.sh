#!/bin/bash

PROTO_DIR=../protos
OUT_DIR=protos

mkdir -p "${OUT_DIR}"

pyenv exec python -m grpc_tools.protoc \
    -I "${PROTO_DIR}" \
    --python_out="${OUT_DIR}" \
    --grpc_python_out="${OUT_DIR}" \
    "${PROTO_DIR}"/*.proto
