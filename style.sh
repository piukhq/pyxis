#!/bin/sh

pipenv shell "\
black . && \
flake8 . && \
isort . && \
xenon --no-assert -a A -m B -b B . && \
mypy .
exit\
"