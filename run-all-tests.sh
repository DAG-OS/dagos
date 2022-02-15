#!/bin/bash

rm .coverage*

tox -e py37
podman run --rm -it -v .:/root/dagos localhost/dagos-test-image:latest

coverage combine
coverage report --ignore-errors --show-missing --skip-covered
