#!/usr/bin/env bash
# Returns sha of current DiffKemp commit
set -eu

cd /diffkemp && git log --format=format:%H | head -n 1
