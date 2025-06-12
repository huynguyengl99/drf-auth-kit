#!/usr/bin/env bash

if [ "$1" == "--fix" ]; then
  ruff check . --fix && black ./auth_kit && toml-sort ./*.toml
else
  ruff check . && black ./auth_kit --check && toml-sort ./*.toml --check
fi
