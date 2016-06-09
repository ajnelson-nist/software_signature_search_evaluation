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

[[ 0 -eq $DEBUG ]] || set -x #For debugging only.

set -e

db="$1"

if [ -z "$db" ]; then
  echo "ERROR:$0:\$1 not provided, must be a SQLite database." >&2
  exit 1
fi

count1=$(sqlite3 "$db" 'SELECT MAX(tally) FROM (SELECT node_id, doc_name, COUNT(*) AS tally FROM ground_truth GROUP BY node_id, doc_name);')
if [ 1 -lt "$count1" ]; then
  echo "ERROR:$0:Multiple truth statements present for a node_id, doc_name pairing." >&2
  exit 1
fi
