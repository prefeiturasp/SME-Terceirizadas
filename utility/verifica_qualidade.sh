#!/usr/bin/env bash
pytest
#flake8 --radon-max-cc 6
flake8
mypy sme_terceirizadas
