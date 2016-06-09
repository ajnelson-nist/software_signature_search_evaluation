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
op="$2"
db2="$3"

case "$op" in
  le | eq )
  ;;
  * )
    echo "ERROR:$0:Unexpected operation in argument 2: '$op'." >&2
    exit 1
  ;;
esac

if [ -z "$db1" ]; then
  echo "ERROR:$0:\$1 not provided, must be a SQLite database." >&2
  exit 1
fi

if [ -z "$db2" ]; then
  echo "ERROR:$0:\$2 not provided, must be a SQLite database." >&2
  exit 1
fi

count1=$(sqlite3 "$db1" 'SELECT COUNT(*) AS tally FROM ground_truth;')
if [ -z "$count1" ]; then
  echo "ERROR:$0:SELECT failed on db1 ('$db1')." >&2
  exit 1
fi

count2=$(sqlite3 "$db2" 'SELECT COUNT(*) AS tally FROM ground_truth;')
if [ -z "$count2" ]; then
  echo "ERROR:$0:SELECT failed on db2 ('$db2')." >&2
  exit 1
fi

case "$op" in
  le  )
    rc=$(test $count1 -le $count2 ; echo $?)
  ;;
  eq )
    rc=$(test $count1 -eq $count2 ; echo $?)
  ;;
esac

if [ 0 -ne $rc ]; then
  echo "ERROR:$0:Count relationship not expected between db1 and db2." >&2
  echo "INFO:$0:\$op=$op" >&2
  echo "INFO:$0:\$db1=$db1" >&2
  echo "INFO:$0:\$db2=$db2" >&2
  echo "INFO:$0:\$count1=$count1" >&2
  echo "INFO:$0:\$count2=$count2" >&2
  exit 1
fi
