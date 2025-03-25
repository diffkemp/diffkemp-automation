#!/usr/bin/env bash
# Compares commits specified in `/commits.txt`, saves results to
# `/commit-output/<project_name>/results.csv`.
set -eu

CONFIG_NAME=$1
REPO_NAME=$1
if [ -z ${IN_DEV_SHELL+x} ]
then
    # We are not in development shell with necessary dependencies,
    # run this script in the development shell.
    nix develop /runner --command bash -c "bash $0 $REPO_NAME"
    exit 0
fi

DIFFKEMP_BIN=`bash /runner/get_diffkemp_bin.sh`
ANALYZER_SCRIPT="/runner/commit_comparison/commit-analysis/analyze.py"
RESULT_DIR="/commit-output/${CONFIG_NAME}"
REPO_PATH="/repos/${REPO_NAME}"
COMMITS_PATH="/commits.txt"
RESULTS_PATH="$RESULT_DIR/results.yml"

mkdir -p $RESULT_DIR
cd $RESULT_DIR
python3.12 $ANALYZER_SCRIPT --diffkemp $DIFFKEMP_BIN $REPO_PATH \
    >> $RESULTS_PATH < $COMMITS_PATH
