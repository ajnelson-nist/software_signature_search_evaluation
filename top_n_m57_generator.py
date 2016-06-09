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

"""Generate a SQL script."""

__version__ = "0.3.0"

def main():
    metadict = dict()
    metadict["rank_variable"] = args.rank_variable
    metadict["where_variable"] = args.where_variable
    metadict["where_variable_value"] = args.where_variable_value

    if args.put_first == "evaluation":
        metadict["order_clause"] = """\
  a.%(rank_variable)s DESC,
  b.%(rank_variable)s DESC,
  a.nonzerolen_doc_count DESC
""" % metadict
    elif args.put_first == "m57":
        metadict["order_clause"] = """\
  b.%(rank_variable)s DESC,
  a.%(rank_variable)s DESC,
  b.nonzerolen_doc_count DESC
""" % metadict
    else:
        raise NotImplementedError("Not sure what to do with put-first argument %r." % args.put_first)

    sql = r"""ATTACH DATABASE 'response_percentiles.db' AS percentiles;

.separator " & " " \\\\\n"

SELECT
  a.searcher_id,
  a.nonzerolen_doc_count,

  a.num_runs_in_ground_truth AS eval_num_runs_in_ground_truth,
  b.num_runs_in_ground_truth AS m57_num_runs_in_ground_truth,

  ROUND(a.%(rank_variable)s,2) AS evaluation_rank,
  100 * ROUND(c.percentile,3) AS evaluation_rank_percentile,

  ROUND(b.%(rank_variable)s,2) AS m57_rank,
  100 * ROUND(d.percentile,3) AS m57_rank_percentile
FROM
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "evaluation") AS a,
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "m57") AS b,
  percentiles.searcher_evaluation_%(rank_variable)s_percentiles AS c,
  percentiles.searcher_m57_%(rank_variable)s_percentiles AS d
WHERE
  a.searcher_id = b.searcher_id AND
  a.searcher_id = c.searcher_id AND
  a.searcher_id = d.searcher_id AND
  a.sequences <> "experiment1" AND
  a.%(where_variable)s = "%(where_variable_value)s"
ORDER BY
%(order_clause)s
LIMIT 20
;""" % metadict

    print(sql)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("rank_variable")
    parser.add_argument("put_first")
    parser.add_argument("where_variable")
    parser.add_argument("where_variable_value")
    args = parser.parse_args()

    main()
