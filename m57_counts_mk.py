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

__version__ = "0.2.0"

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import m57_meta

def main():
    global args

    rules_map = dict()

    for sequence in m57_meta.MACHINE_TAG_SEQUENCES:
        for node_id in m57_meta.MACHINE_TAG_SEQUENCES[sequence]:
            metadict = dict()
            metadict["node_id"] = node_id
            metadict["fiout_path"] = os.path.join(args.walk_root, node_id, "make_fiwalk_dfxml_all.sh", "fiout.dfxml")
            metadict["rxdb_path"] = os.path.join(args.walk_root, node_id, "format_registry_single_state.sh", "registry_single_state.db")

            metadict["filesystem_txt"] = "m57_counts/%(node_id)s/filesystem.txt" % metadict
            rule = """\
%(filesystem_txt)s: \\
  Objects.py \\
  %(fiout_path)s \\
  dfxml.py \\
  m57_counts_map_filesystem.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) m57_counts_map_filesystem.py $(DEBUG_FLAG) %(fiout_path)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $$(dirname $@)/$$(basename $@)
""" % metadict
            rules_map[metadict["filesystem_txt"]] = rule

            metadict["registry_txt"] = "m57_counts/%(node_id)s/registry.txt" % metadict
            rule = """\
%(registry_txt)s: \\
  %(rxdb_path)s \\
  m57_counts_map_registry.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) m57_counts_map_registry.py $(DEBUG_FLAG) %(rxdb_path)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $$(dirname $@)/$$(basename $@)
""" % metadict
            rules_map[metadict["registry_txt"]] = rule

    with open(args.out_mk, "w") as out_fh:
        out_fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
PYTHON3 ?= python3.4

all:""")
        for target in sorted(rules_map.keys()):
            out_fh.write(" \\\n  %s" % target)
        out_fh.write("\n")

        for target in sorted(rules_map.keys()):
            out_fh.write("\n")
            out_fh.write(rules_map[target])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("walk_root")
    parser.add_argument("out_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
