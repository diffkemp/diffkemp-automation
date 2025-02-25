#!/usr/bin/env bash
# Adds automatic checking and comparison of new versions to cron.
BIN_PATH=`which diffkemp-automation-compare`
(crontab -l ; echo "00 00 * * * ${BIN_PATH}  1>> `pwd`/compare.log 2>> `pwd`/compare.log") | crontab -
