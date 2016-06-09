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

db1="$1"
db2="$2"
out_log="$3"

if [ -z "$db1" ]; then
  echo "ERROR:$0:\$1 not provided, must be a SQLite database." >&2
  exit 1
fi

if [ -z "$db2" ]; then
  echo "ERROR:$0:\$2 not provided, must be a SQLite database." >&2
  exit 1
fi

sqlite3 <<EOF
ATTACH DATABASE '$db1' AS db1;
ATTACH DATABASE '$db2' AS db2;

SELECT DISTINCT
  doc_name
FROM
  db2.ground_truth_positive
WHERE
  doc_name NOT IN (
    SELECT DISTINCT
      doc_name
    FROM
      db1.ground_truth_positive
  )
;
EOF
