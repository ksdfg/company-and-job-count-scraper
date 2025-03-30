#!/usr/bin/env bash

set -ex

mypy ../.
black ../. --check
isort --check-only ../.
flake8 ../.