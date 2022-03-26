#!/bin/bash
set -euxo pipefail

LOG_FILE="podman-build.log"
rm -f $LOG_FILE

dagos env deploy --container tests/data/environments/dagos-test-image.yml 2>&1 | tee -a $LOG_FILE

podman build --rm -f Dockerfile . 2>&1 | tee -a $LOG_FILE

IMAGE_ID=$(tail -n 1 $LOG_FILE)

podman tag "$IMAGE_ID" localhost/dagos-test-image
