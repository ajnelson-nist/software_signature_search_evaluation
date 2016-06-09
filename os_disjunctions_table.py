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

__version__ = "0.3.0"

import logging
import os
import pickle

#Thousands separation <https://stackoverflow.com/a/1823101>
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    osnames = None
    thetable = None
    with open(args.in_pickle, "rb") as in_fh:
        unpickler = pickle.Unpickler(in_fh)
        in_dict = unpickler.load()
        osnames = in_dict["osnames"]
        thetable = in_dict["thetable"]

    #Write to one output file.  Write other output to /dev/null.
    #(This is an artifact of the initial implementation, where HTML and Latex code were kept side by side.)
    if args.latex:
        output_html = open(os.devnull, "w")
        output_latex = open(args.out_file, "w")
    elif args.html:
        output_html = open(args.out_file, "w")
        output_latex = open(os.devnull, "w")

    #HTML
    output_html.write("""\
<table>
  <thead>
""")
    output_html.write("""\
    <tr>
      <th></th>
""") #Top-left cell: blank
    for osname in osnames:
        output_html.write("""\
      <th>%s</th>
""" % osname)
    output_html.write("""\
    </tr>
  </thead>
  <tfoot></tfoot>
  <tbody>
""")

    #LaTeX
    output_latex.write(" & ") #Top-left cell: blank
    output_latex.write(" & ".join(osnames))
    output_latex.write(" \\\\\n")
    
    #Divide between table header and table body
    output_latex.write("\\midrule\n")

    sorted_pairs_shown = set()

    for osnamerow in osnames:
        html_body_row = []
        html_body_row.append("    <tr>")
        html_body_row.append("<th>%s</th>" % osnamerow)

        latex_body_row = []
        latex_body_row.append(osnamerow)

        for osnamecol in osnames:
            sorted_pair = tuple(sorted([osnamerow, osnamecol]))
            if sorted_pair in sorted_pairs_shown:
                formatted_number = ""
            else:
                formatted_number = locale.format("%d", thetable[(osnamerow,osnamecol)], grouping=True)
            html_body_row.append("<td>%s</td>" % formatted_number)
            latex_body_row.append(formatted_number)
            sorted_pairs_shown.add(sorted_pair)

        html_body_row.append("</tr>\n")
        latex_body_row[-1] += " \\\\\n"

        output_html.write("".join(html_body_row))
        output_latex.write(" & ".join(latex_body_row))
        
    output_html.write("""\
  </tbody>
</table>
""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--latex", action="store_true")
    parser.add_argument("in_pickle")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
