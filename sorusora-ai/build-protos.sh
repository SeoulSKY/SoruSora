#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path-to-protos-dir>"
    exit 1
fi

OUT_DIR=src/protos

PATH=${PATH}:./node_modules/.bin

npm install -D

mkdir -p "${OUT_DIR}"

# Generate JavaScript code for gRPC
grpc_tools_node_protoc \
    --js_out=import_style=commonjs,binary:"${OUT_DIR}" \
    --grpc_out=grpc_js:"${OUT_DIR}" \
    --plugin=protoc-gen-grpc=./node_modules/.bin/grpc_tools_node_protoc_plugin \
    -I "$1" \
    "$1"/*.proto

# Generate TypeScript code (d.ts) for gRPC
grpc_tools_node_protoc \
    --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
    --ts_out=grpc_js:"${OUT_DIR}" \
    -I "$1" \
    "$1"/*.proto
