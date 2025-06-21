#!/usr/bin/env bash

pytest --cov=auth_kit --cov-report= sandbox

pytest --cov=auth_kit --cov-append --cov-report=term-missing sandbox_extras/custom_auth
