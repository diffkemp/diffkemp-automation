#!/usr/bin/env bash
# Script builds DiffKemp
set -eu

if [ -z ${IN_DEV_SHELL+x} ]
then
    # We are not in development shell with necessary dependencies,
    # run this script in the development shell.
    nix develop /runner --command bash -c "bash $0"
    exit 0
fi

cd /diffkemp
git pull
cmake -S . -B build -GNinja -DBUILD_VIEWER=On
ninja -C build
