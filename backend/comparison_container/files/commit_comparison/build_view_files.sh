#!/usr/bin/env bash
# Launches DiffKemp viewer and prepares results for visualisation,
# the files prepared for visualization are saved in `/commit-view/` directory,
# it contains subdirectories named `<project>/<commit>`, where <project> is the
# name of project and <commit> is SHA of evaluated commit.
set -eu

if [ -z ${IN_DEV_SHELL+x} ]
then
    # We are not in development shell with necessary dependencies,
    # run this script in the development shell.
    nix develop /runner --command bash -c "bash $0"
    exit 0
fi

DIFFKEMP_BIN=`bash /runner/get_diffkemp_bin.sh`
RESULTS_DIFFKEMP_OUT="/commit-output/*/result/*/diffkemp-out.yaml"
OUTPUT_DIR="/commit-view"
DIFFKEMP_VIEWER_BUILD="/diffkemp/view/build"

# Iterate over all results (compared pairs)
for result in ${RESULTS_DIFFKEMP_OUT}
do
    # If all functions in all project were evaluated as equal,
    # the `diffkemp-out.yaml` file is not created and RESULTS_DIFFKEMP_OUT will
    # be "/commit-output/*/result/*/diffkemp-out.yaml". So the path will not
    # exist, so skip it.
    if [ ! -e ${result} ]
    then
        continue
    fi
    # Path to directory with result
    result_path=`dirname $result`
    commit=`basename $result_path`
    project_name=`dirname $result_path | xargs dirname | xargs basename`

    mkdir -p /commit-view/${project_name}
    ${DIFFKEMP_BIN} view ${result_path} &
    viewer_pid=$!
    sleep 5
    cp -r ${DIFFKEMP_VIEWER_BUILD} ${OUTPUT_DIR}/${project_name}/${commit}
    kill -9 $viewer_pid
done