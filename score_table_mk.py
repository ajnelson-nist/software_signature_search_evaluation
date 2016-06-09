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

import os
import logging

_logger = logging.getLogger(os.path.basename(__file__))

import magnum_opus

def main():
    rules = dict()

    metadict = dict()
    metadict["dataset"] = "training"
    for sequence in magnum_opus._sequences:
        metadict["sequence"] = sequence
        for n_grams in magnum_opus._n_grams:
            metadict["n_grams"] = n_grams
            for stop_list_n_gram_strategy in magnum_opus._stop_list_n_gram_strategies:
                metadict["stop_list_n_gram_strategy"] = stop_list_n_gram_strategy
                for path in magnum_opus._paths:
                    metadict["path"] = path
                    for docs_by in magnum_opus._docs_bys:
                        metadict["docs_by"] = docs_by
                        for combinator in magnum_opus._combinators:
                            if combinator == "inconsistent":
                                #This combinator isn't used after stop list construction.
                                continue
                            metadict["combinator"] = combinator 
                            for stop_list in magnum_opus._stop_lists:
                                metadict["stop_list"] = stop_list
                                for subset in ["all", "firefox", "msoffice"]:
                                    #Build evaluation exploratory tables
                                    metadict["subset"] = subset
                                    metadict["subset_flag"] = {
                                      "firefox":  "--only-firefox",
                                      "msoffice": "--only-msoffice",
                                      "all":      ""
                                    }[subset]
                                    metadict["search_score_manifest"] = "search_scores/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/pickle_manifest.txt" % metadict
                                    metadict["score_table_html"] = "score_table/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/subset_%(subset)s/score_table.html" % metadict
                                    rules[metadict["score_table_html"]] = """\
%(score_table_html)s: \\
  PY3_MATPLOTLIB \\
  score_table.py \\
  %(search_score_manifest)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) score_table.py $(DEBUG_FLAG) %(subset_flag)s %(search_score_manifest)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

    with open(args.output_mk, "w") as fh:
        fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
PYTHON3 ?= python3.4

all: \\
  extra

.PHONY: extra

extra:""")
        for target in sorted(rules.keys()):
            fh.write(" \\\n  %s" % target)
        fh.write("\n")

        for target in sorted(rules.keys()):
            fh.write("\n")
            fh.write(rules[target])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("output_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
