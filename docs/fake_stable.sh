#!/usr/bin/env sh
# Pretend to be a stable build runner of readthedocs
# https://docs.readthedocs.io/en/stable/reference/environment-variables.html
READTHEDOCS='True' READTHEDOCS_VERSION_NAME='stable' make html
