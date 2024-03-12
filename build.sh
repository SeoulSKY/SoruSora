#!/bin/bash

PATHS=("sorusora" "sorusora-ai")

# Function to build protos in a directory
build_protos() {
  echo "Building project in $1"
  pushd "$1" > /dev/null || return
  chmod +x build.sh
  ./build.sh
  popd > /dev/null || return
}

for path in "${PATHS[@]}"; do
  build_protos "${path}" || true
done
