#!/bin/sh

pipenv shell "\
black . && \
isort . && \
xenon --no-assert -a A -m B -b B . && \
pylint **/*.py  && \
mypy .
exit\
"