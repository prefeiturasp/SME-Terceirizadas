#!/usr/bin/env bash
echo "Pytest..."
pytest
echo "Flake8..."
flake8
echo "Mypy..."
mypy sme_terceirizadas
