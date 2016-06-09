#!/usr/bin/env python3

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

__version__ = "0.1.0"

import logging
import os
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    rules = dict()

    edges = set()
    with sqlite3.connect(args.namedsequence_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""\
SELECT
  *
FROM
  namedsequence
WHERE
  NOT predecessor_sliceid IS NULL AND
  (
    sequencelabel LIKE 'repeated-%' OR
    sequencelabel LIKE 'installclose-%'
  )
;""")
        for row in cursor:
            node_id = "%s-%s-%d" % (row["osetid"], row["appetid"], row["sliceid"])
            predecessor_node_id = "%s-%s-%d" % (row["predecessor_osetid"], row["predecessor_appetid"], row["predecessor_sliceid"])
            edges.add((predecessor_node_id, node_id))

    for edge in sorted(edges):
        metadict = dict()
        metadict["predecessor_nodeid"] = edge[0]
        metadict["nodeid"] = edge[1]
        metadict["registry_diff_db"] = "by_edge/%(predecessor_nodeid)s/%(nodeid)s/make_registry_diff_db.sh/registry_new_cellnames.db" % metadict
        rules[metadict["registry_diff_db"]] = """\
%(registry_diff_db)s: \\
  deltas.db \\
  deltas_db_to_edge_db.py \\
  differ_func_library.py \\
  registry_single_state_schema.sql
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	sqlite3 $$(dirname $@)/_$$(basename $@) < registry_single_state_schema.sql
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) deltas_db_to_edge_db.py deltas.db %(predecessor_nodeid)s %(nodeid)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

    with open(args.out_mk, "w") as out_fh:
        out_fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
GTIME ?= /opt/local/bin/gtime
PYTHON3 ?= python3.4

all:""")
        for target in sorted(rules.keys()):
            out_fh.write(" \\\n  %s" % target)
        out_fh.write("\n")

        for target in sorted(rules.keys()):
            out_fh.write("\n")
            out_fh.write(rules[target])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("namedsequence_db")
    parser.add_argument("out_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
