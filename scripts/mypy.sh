#!/usr/bin/env bash

set -e

export PYTHONPATH="sandbox"
export MYPYPATH='.'


# Cleaning existing cache:
rm -rf .mypy_cache

if [ "$1" == "--sandbox" ]; then
  export DJANGO_SETTINGS_MODULE=config.settings.dev
  mypy sandbox
else
  export DJANGO_SETTINGS_MODULE=auth_kit.app_settings
  mypy auth_kit
fi
