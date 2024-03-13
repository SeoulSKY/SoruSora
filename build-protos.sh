#!/bin/bash

SCRIPT_PATHS=("sorusora" "sorusora-ai")

EXEC=build-protos.sh

for path in "${SCRIPT_PATHS[@]}"; do
  echo "Building Protocol Buffer for ${path}"

  pushd "${path}" > /dev/null || return
  chmod +x "${EXEC}"
  ./"${EXEC}"
  popd > /dev/null || return
done
