#!/usr/bin/env bash

if [ "$1" == "--fix" ]; then
  ruff check . --fix && black ./auth_kit ./sandbox ./sandbox_extras && toml-sort ./*.toml
else
  ruff check . && black ./auth_kit ./sandbox ./sandbox_extras --check && toml-sort ./*.toml --check
fi
