#!/bin/bash

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

#This script runs the global diskprint Registry analysis.  It includes tuning parameters for Barrel.

set -x
set -e

NUM_JOBS=16

date
#Download data and generate the Makefiles that end up orchestrating most of the work.
time make -j $NUM_JOBS magnum_opus.mk mult_results.mk

date
make --dry-run --keep-going | egrep '^mv ' | awk '{print $(NF)}' | sort > to-make.all.log

#Use temporary directory for SQLite temp databases (to keep home directory from filling up).
#  Temp dir tip c/o: https://stackoverflow.com/a/10395983
date
#Run demo-prereqs first to see if there is any issue in processing a subset of the repetitions.
TMPDIR="$PWD/tmp" time make --keep-going -j $NUM_JOBS demo-prereqs >make.demo-prereqs.log 2>&1
date
TMPDIR="$PWD/tmp" time make --keep-going -j $NUM_JOBS >make.all.log 2>&1 || time make >make.all.fail.log 2>&1
date
