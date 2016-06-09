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

set -x
set -e

this_script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
"${this_script_dir}/brownzipf/deps/install_dependent_packages-osx-10.9.sh"
"${this_script_dir}/diskprint_workflow/deps/install_dependent_packages-osx-10.9.sh"

sudo port install \
  p7zip \
  py27-pandas \
  py27-pygraphviz \
  py34-psycopg2 \
  py34-pandas \
  py34-seaborn
