#!/bin/bash

rm .coverage*

tox -e py37
podman run --rm -it -v .:/root/dagos localhost/dagos-test-image:latest

coverage combine
coverage report --show-missing --skip-covered
