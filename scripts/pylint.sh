#!/bin/bash

ROOT_DIR="$(git rev-parse --show-toplevel)"

export PYTHONPATH="${PYTHONPATH}:${ROOT_DIR}/src"

pylint --rcfile="${ROOT_DIR}/.pylintrc" "${ROOT_DIR}/src/*.py"
