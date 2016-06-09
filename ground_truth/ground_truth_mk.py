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

__version__ = "0.1.1"

import os
import logging
import collections

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    rules = dict()
    rules_check = [
      "check_ground_truth_uniqueness.log",
      "check_versions_counts_consistent.log",
      "data_m57/check_ground_truth_negative.log",
      "data_training/check_ground_truth_positive_doc_names.log"
    ]
    rules_dist = list()
    flag_rollups = collections.defaultdict(list) #Key: target file.  Value: List of prerequisites to executing "touch $@".

    rules[".PHONY"] = ".PHONY: check dist\n"

    #Define the ground truth positive databases with their own more-specialized rules.
    for docs_by in ["app", "osapp"]:
        metadict = dict()
        metadict["docs_by"] = docs_by

        metadict["evaluation_distinct_ground_truth_positive_db"] = "data_evaluation/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db" % metadict
        rules[metadict["evaluation_distinct_ground_truth_positive_db"]] = """\
%(evaluation_distinct_ground_truth_positive_db)s: \\
  ground_truth_evaluation_image_%(docs_by)s.sql
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	sqlite3 "$$(dirname $@)/_$$(basename $@)" < $<
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["evaluation_grouped_ground_truth_positive_db"] = "data_evaluation/docs_by_%(docs_by)s/versions_grouped/ground_truth_positive.db" % metadict
        rules[metadict["evaluation_grouped_ground_truth_positive_db"]] = """\
%(evaluation_grouped_ground_truth_positive_db)s: \\
  data_evaluation/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  ground_truth_grouped.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) ground_truth_grouped.py $(DEBUG_FLAG) data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db data_evaluation/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["m57_distinct_ground_truth_positive_db"] = "data_m57/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db" % metadict
        rules[metadict["m57_distinct_ground_truth_positive_db"]] = """\
%(m57_distinct_ground_truth_positive_db)s: \\
  ../experiments/m57_roussev_dfrws12/application_appearances.py \\
  ../experiments/m57_roussev_dfrws12/db.py \\
  ../m57_meta.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) ../experiments/m57_roussev_dfrws12/db.py $(DEBUG_FLAG) %(docs_by)s "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["m57_grouped_ground_truth_positive_db"] = "data_m57/docs_by_%(docs_by)s/versions_grouped/ground_truth_positive.db" % metadict
        rules[metadict["m57_grouped_ground_truth_positive_db"]] = """\
%(m57_grouped_ground_truth_positive_db)s: \\
  data_m57/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  ground_truth_grouped.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) ground_truth_grouped.py $(DEBUG_FLAG) data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db data_m57/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["training_distinct_ground_truth_positive_db"] = "data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db" % metadict
        rules[metadict["training_distinct_ground_truth_positive_db"]] = """\
%(training_distinct_ground_truth_positive_db)s: \\
  ground_truth.py \\
  ../sequences/namedsequence.db \\
  ../slice.db \\
  ../differ_func_library.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) ground_truth.py --by-%(docs_by)s $(DEBUG_FLAG) ../sequences/namedsequence.db ../slice.db "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["training_grouped_ground_truth_positive_db"] = "data_training/docs_by_%(docs_by)s/versions_grouped/ground_truth_positive.db" % metadict
        rules[metadict["training_grouped_ground_truth_positive_db"]] = """\
%(training_grouped_ground_truth_positive_db)s: \\
  data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  ground_truth_grouped.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) ground_truth_grouped.py $(DEBUG_FLAG) "$<" "$<" "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        metadict["training_check_ground_truth_positive_doc_names_log"] = "data_training/docs_by_%(docs_by)s/versions_grouped/check_ground_truth_positive_doc_names.log" % metadict
        rules[metadict["training_check_ground_truth_positive_doc_names_log"]] = """\
%(training_check_ground_truth_positive_doc_names_log)s: \\
  data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db \\
  data_training/docs_by_%(docs_by)s/versions_grouped/ground_truth_positive.db \\
  check_ground_truth_positive_doc_names.sh
	rm -f "$$(dirname $@)/_$$(basename $@)"
	./check_ground_truth_positive_doc_names.sh data_training/docs_by_%(docs_by)s/versions_distinct/ground_truth_positive.db data_training/docs_by_%(docs_by)s/versions_grouped/ground_truth_positive.db > "$$(dirname $@)/_$$(basename $@)"
	test 0 -eq $$(cat "$$(dirname $@)/_$$(basename $@)" | wc -l) || (echo "ERROR:ground_truth.mk:Documents found in grouped database that weren't in the distinct database." >&2 ; exit 1)
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict
        flag_rollups["data_training/check_ground_truth_positive_doc_names.log"].append(metadict["training_check_ground_truth_positive_doc_names_log"])

        for dataset in ["evaluation", "m57"]:
            metadict["dataset"] = dataset
            metadict["check_versions_counts_consistent_log"] = "data_%(dataset)s/docs_by_%(docs_by)s/check_versions_counts_consistent.log" % metadict
            rules[metadict["check_versions_counts_consistent_log"]] = """\
%(check_versions_counts_consistent_log)s: \\
  check_versions_counts_consistent.sh \\
  data_%(dataset)s/docs_by_%(docs_by)s/versions_distinct/ground_truth.db \\
  data_%(dataset)s/docs_by_%(docs_by)s/versions_grouped/ground_truth.db
	./check_versions_counts_consistent.sh data_%(dataset)s/docs_by_%(docs_by)s/versions_distinct/ground_truth.db le data_%(dataset)s/docs_by_%(docs_by)s/versions_grouped/ground_truth.db
	touch $@
""" % metadict
            flag_rollups["check_versions_counts_consistent.log"].append(metadict["check_versions_counts_consistent_log"])

    rules["data_training/docs_by_app/check_versions_counts_consistent.log"] = """\
data_training/docs_by_app/check_versions_counts_consistent.log: \\
  check_versions_counts_consistent.sh \\
  data_training/docs_by_app/versions_distinct/ground_truth.db \\
  data_training/docs_by_app/versions_grouped/ground_truth.db
	./check_versions_counts_consistent.sh data_training/docs_by_app/versions_distinct/ground_truth.db eq data_training/docs_by_app/versions_grouped/ground_truth.db
	touch $@
"""
    flag_rollups["check_versions_counts_consistent.log"].append("data_training/docs_by_app/check_versions_counts_consistent.log")

    rules["data_training/docs_by_osapp/check_versions_counts_consistent.log"] = """\
data_training/docs_by_osapp/check_versions_counts_consistent.log: \\
  check_versions_counts_consistent.sh \\
  data_training/docs_by_osapp/versions_distinct/ground_truth.db \\
  data_training/docs_by_osapp/versions_grouped/ground_truth.db
	rm -f "$$(dirname $@)/_$$(basename $@)"
	./check_versions_counts_consistent.sh data_training/docs_by_osapp/versions_distinct/ground_truth.db eq data_training/docs_by_osapp/versions_grouped/ground_truth.db
	touch $@
"""
    flag_rollups["check_versions_counts_consistent.log"].append("data_training/docs_by_osapp/check_versions_counts_consistent.log")

    for docs_by in ["app", "osapp"]:
        for versions in ["distinct", "grouped"]:
            metadict = dict()
            metadict["docs_by"] = docs_by
            metadict["versions"] = versions
            metadict["check_ground_truth_negative_log"] = "data_m57/docs_by_%(docs_by)s/versions_%(versions)s/check_ground_truth_negative.log" % metadict
            rules[metadict["check_ground_truth_negative_log"]] = """\
%(check_ground_truth_negative_log)s: \\
  data_m57/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db \\
  check_ground_truth_negative_m57.sh
	./check_ground_truth_negative_m57.sh $<
	touch $@
""" % metadict
            flag_rollups["data_m57/check_ground_truth_negative.log"].append(metadict["check_ground_truth_negative_log"])

    param_tuples = []
    for dataset in ["evaluation", "m57", "training"]:
        for docs_by in ["app", "osapp"]:
            for versions in ["distinct", "grouped"]:
                param_tuples.append((dataset, docs_by, versions))

    for param_tuple in param_tuples:
        metadict = dict()
        metadict["dataset"] = param_tuple[0]
        metadict["docs_by"] = param_tuple[1]
        metadict["versions"] = param_tuple[2]

        metadict["ground_truth_positive_db"] = "data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db" % metadict
        metadict["training_ground_truth_positive_db"] = "data_training/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db" % metadict

        metadict["ground_truth_db"] = "data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db" % metadict
        if dataset == "m57":
            rules[metadict["ground_truth_db"]] = """\
%(ground_truth_db)s: \\
  ../m57_meta.py \\
  data_m57/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db \\
  data_training/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db \\
  m57_ground_truth_completion.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) m57_ground_truth_completion.py data_training/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db data_m57/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth_positive.db "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict
        else:
            rules[metadict["ground_truth_db"]] = """\
%(ground_truth_db)s: \\
  %(ground_truth_positive_db)s \\
  %(training_ground_truth_positive_db)s \\
  cartesian_ground_truth_completion.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) cartesian_ground_truth_completion.py %(training_ground_truth_positive_db)s $< "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict

        if metadict["dataset"] == "evaluation":
            for use_short_names in [False, True]:
                if metadict["versions"] == "grouped" and use_short_names == True:
                    #Short names for the grouped ground truth table haven't been entered.
                    continue
                metadict["use_short_names_flag"] = "--use-short-names" if use_short_names else ""
                metadict["use_short_names_suffix"] = "-short_names" if use_short_names else ""
                metadict["ground_truth_tex"] = "data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth%(use_short_names_suffix)s.tex" % metadict
                rules[metadict["ground_truth_tex"]] = """\
%(ground_truth_tex)s: \\
  %(ground_truth_db)s \\
  ../etid_to_productname.db \\
  tablify_evaluation_ground_truth.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) tablify_evaluation_ground_truth.py %(use_short_names_flag)s ../etid_to_productname.db $< tex "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict
                rules_dist.append(metadict["ground_truth_tex"])

        metadict["check_ground_truth_uniqueness_log"] = "data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/check_ground_truth_uniqueness.log" % metadict
        rules[metadict["check_ground_truth_uniqueness_log"]] = """\
%(check_ground_truth_uniqueness_log)s: \\
  %(ground_truth_db)s \\
  check_ground_truth_uniqueness.sh
	./check_ground_truth_uniqueness.sh $<
	touch $@
""" % metadict
        flag_rollups["check_ground_truth_uniqueness.log"].append(metadict["check_ground_truth_uniqueness_log"])

        #Check that sets of doc names match between training and M57 and evaluation
        if metadict["dataset"] != "training":
            for versions in ["distinct", "grouped"]:
                metadict["versions"] = versions
                metadict["check_ground_truth_doc_names_log"] = "data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/check_ground_truth_doc_names.log" % metadict
                #The possible-superset database needs to come as the second argument to check_ground_truth_doc_names.sh.
                rules[metadict["check_ground_truth_doc_names_log"]] = """\
%(check_ground_truth_doc_names_log)s: \\
  data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db \\
  data_training/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db \\
  check_ground_truth_doc_names.sh
	rm -f "$$(dirname $@)/_$$(basename $@)"
	./check_ground_truth_doc_names.sh data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db data_training/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db > "$$(dirname $@)/_$$(basename $@)"
	test 0 -eq $$(cat "$$(dirname $@)/_$$(basename $@)" | wc -l) || (echo "ERROR:ground_truth.mk:Documents found in training database that weren't in the %(dataset)s database." >&2 ; exit 1)
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
""" % metadict
                flag_rollups["check_ground_truth_doc_names.log"].append(metadict["check_ground_truth_doc_names_log"])

    rules["data_evaluation/docs_by_app/versions_distinct/appearance_order.tex"] = """\
data_evaluation/docs_by_app/versions_distinct/appearance_order.tex: \\
  data_evaluation/docs_by_app/versions_distinct/ground_truth_positive.db \\
  ../etid_to_productname.db \\
  first_appearance_evaluation_image.py
	mkdir -p $$(dirname $@)
	rm -f "$$(dirname $@)/_$$(basename $@)"
	$(PYTHON3) first_appearance_evaluation_image.py ../etid_to_productname.db $< tex "$$(dirname $@)/_$$(basename $@)"
	mv "$$(dirname $@)/_$$(basename $@)" "$@"
"""
    rules_dist.append("data_evaluation/docs_by_app/versions_distinct/appearance_order.tex")

    for target in flag_rollups.keys():
        rule_parts = [target + ":"]
        for prerequisite in sorted(flag_rollups[target]):
            rule_parts.append(" \\\n  %s" % prerequisite)
        rule_parts.append("\n\ttouch $@")
        rule_parts.append("\n")
        rules[target] = "".join(rule_parts)

    _logger.debug("rules_dist = %r." % rules_dist)
    for (phony_target, phony_list) in [
      ("check", rules_check),
      ("dist", rules_dist)
    ]:
        rule_parts = [phony_target + ":"]
        for target in phony_list:
            rule_parts.append(" \\\n  %s" % target)
        rule_parts.append("\n")
        rules[phony_target] = "".join(rule_parts)

    with open(args.out_mk, "w") as fh:
        fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
PYTHON3 ?= python3.4

all:""")
        for target in sorted(rules.keys()):
            if target in [".PHONY", "clean", "check", "dist"]:
                continue
            if target in rules_dist:
                continue
            fh.write(" \\\n  %s" % target)
        fh.write("\n")

        for target in sorted(rules.keys()):
            fh.write("\n")
            fh.write(rules[target])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("out_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
