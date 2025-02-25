#!/usr/bin/env bash
# Compares project versions specified in `/config.yml`, saves results to
# `/version-output` dir.
set -eu

REPO_NAME=$1
if [ -z ${IN_DEV_SHELL+x} ]
then
    # We are not in development shell with necessary dependencies,
    # run this script in the development shell.
    nix develop /runner --command bash -c "bash $0 $REPO_NAME"
    exit 0
fi

DIFFKEMP_BIN=`bash /runner/get_diffkemp_bin.sh`
ANALYZER_SCRIPT="/runner/version_comparison/version-analysis/analyze.py"
OUTPUT="/version-output"
PROJECT_CONFIG="/config.yml"
REPO_PATH="/repos/${REPO_NAME}"

python3 ${ANALYZER_SCRIPT} \
    --diffkemp ${DIFFKEMP_BIN} \
    --output ${OUTPUT} \
    --sources /repos \
    --verbose \
    ${PROJECT_CONFIG}
