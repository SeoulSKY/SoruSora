#!/bin/bash

PATHS=("sorusora" "sorusora-ai")

EXEC=build-protos.sh

# Function to build protos in a directory
build_protos() {
  echo "Building project in $1"
  pushd "$1" > /dev/null || return
  chmod +x "${EXEC}"
  ${EXEC}
  popd > /dev/null || return
}

for path in "${PATHS[@]}"; do
  build_protos "${path}" || true
done
