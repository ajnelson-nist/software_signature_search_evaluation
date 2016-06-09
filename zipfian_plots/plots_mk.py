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

import sys

def main():
    rules = dict()
    for stop_list_n_gram_strategy in ["raw_filter", "n_gram_blacklist", "n_gram_threshold"]:
        for stop_list in ["none", "baseline", "bp", "bpi"]:
            metadict = dict()
            metadict["stop_list_n_gram_strategy"] = stop_list_n_gram_strategy
            metadict["stop_list"] = stop_list 
            metadict["query_list_txt"] = "stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/stop_list_%(stop_list)s/experiment1-20.txt" % metadict
            rules[metadict["query_list_txt"]] = """\
%(query_list_txt)s: \\
  ../query/data_evaluation/n_grams_1/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_raw/docs_by_app/stop_list_%(stop_list)s/experiment1-20.db \\
  ../query/data_evaluation/n_grams_2/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_raw/docs_by_app/stop_list_%(stop_list)s/experiment1-20.db \\
  ../query/data_evaluation/n_grams_3/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_raw/docs_by_app/stop_list_%(stop_list)s/experiment1-20.db \\
  ../query/data_evaluation/n_grams_all/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_raw/docs_by_app/stop_list_%(stop_list)s/experiment1-20.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	for x in $^; do echo $$x >> $$(dirname $@)/_$$(basename $@) ; done
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

            for output_format in ["pdf", "png"]:
                metadict["output_format"] = output_format
                metadict["plot"] = "stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/stop_list_%(stop_list)s/experiment1-20.%(output_format)s" % metadict
                rules[metadict["plot"]] = """\
%(plot)s: \\
  %(query_list_txt)s \\
  n_gram_rank_dist.py
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) n_gram_rank_dist.py $(DEBUG_FLAG) --out-format=png $< $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

    sys.stdout.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
PYTHON3 ?= python3.4

all: \\
  all.done.log

all.done.log:""")
    for target in sorted(rules.keys()):
        sys.stdout.write(" \\\n  %s" % target)
    sys.stdout.write("\n\ttouch $@")
    sys.stdout.write("\n")

    for target in sorted(rules.keys()):
        sys.stdout.write("\n")
        sys.stdout.write(rules[target])

if __name__ == "__main__":
    main()
