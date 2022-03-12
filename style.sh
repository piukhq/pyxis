#!/bin/sh

pipenv run black . && \
pipenv run flake8 . && \
pipenv run isort . && \
pipenv run xenon --no-assert --max-average A --max-modules B --max-absolute B .
