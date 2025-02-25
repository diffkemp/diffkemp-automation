#!/usr/bin/env bash
# Builds container image
podman build --ulimit nofile=65536:65536 -t diffkemp-automation `dirname $0`
