#!/bin/bash

PROTO_DIR=../protos
OUT_DIR=src/protos

mkdir -p ${OUT_DIR}

# Generate JavaScript code for gRPC
grpc_tools_node_protoc \
    --js_out=import_style=commonjs,binary:${OUT_DIR} \
    --grpc_out=grpc_js:${OUT_DIR} \
    --plugin=protoc-gen-grpc=./node_modules/.bin/grpc_tools_node_protoc_plugin \
    -I ${PROTO_DIR} \
    ${PROTO_DIR}/*.proto

# Generate TypeScript code (d.ts) for gRPC
grpc_tools_node_protoc \
    --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
    --ts_out=grpc_js:${OUT_DIR} \
    -I ${PROTO_DIR} \
    ${PROTO_DIR}/*.proto

# Generate JavaScript code
tsc
