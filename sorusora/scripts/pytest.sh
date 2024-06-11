#!/bin/bash

ROOT_DIR="$(git rev-parse --show-toplevel)/sorusora"

export PYTHONPATH="${PYTHONPATH}:${ROOT_DIR}/src"

pytest "${ROOT_DIR}/tests"
