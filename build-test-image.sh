#!/bin/bash
set -euxo pipefail

LOG_FILE="podman-build.log"

podman build --rm -f Dockerfile . | tee $LOG_FILE

IMAGE_ID=$(tail -n 1 $LOG_FILE)
rm $LOG_FILE

podman tag "$IMAGE_ID" localhost/dagos-test-image
