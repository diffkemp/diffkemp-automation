#!/usr/bin/env bash
# Launches DiffKemp viewer and prepares results for visualisation,
# the files prepared for visualization are saved in `/version-view/` directory,
# it contains subdirectories named `<project>/<v1>-<v2>`, where <v1> and <v2>
# are the compared versions/tags and <project> is the project name.
set -eu

if [ -z ${IN_DEV_SHELL+x} ]
then
    # We are not in development shell with necessary dependencies,
    # run this script in the development shell.
    nix develop /runner --command bash -c "bash $0"
    exit 0
fi


DIFFKEMP_BIN=`bash /runner/get_diffkemp_bin.sh`
RESULTS_DIFFKEMP_OUT="/version-output/*/*/diffkemp-out.yaml"
OUTPUT_DIR="/version-view"
DIFFKEMP_VIEWER_BUILD="/diffkemp/view/build"

# Iterate over all results (compared pairs)
for result in ${RESULTS_DIFFKEMP_OUT}
do
    # Check that the result exists
    if [ ! -e ${result} ]
    then
        continue
    fi
    # Path to directory with result
    result_path=`dirname $result`
    # Extracting subpath form -- `project/<v1>-<v2>`
    dir_subpath=${result_path#/version-output/}
    project_name=`dirname $dir_subpath`
    versions=`basename $dir_subpath`

    mkdir -p ${OUTPUT_DIR}/${project_name}
    ${DIFFKEMP_BIN} view $result_path &
    viewer_pid=$!
    sleep 5
    cp -r ${DIFFKEMP_VIEWER_BUILD} ${OUTPUT_DIR}/${project_name}/${versions}
    kill -9 $viewer_pid
done
