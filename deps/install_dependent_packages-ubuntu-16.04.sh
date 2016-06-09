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
"${this_script_dir}/brownzipf/deps/install_dependent_packages-ubuntu-16.04.sh"

printf "\nWARNING:$(basename "${BASH_SOURCE[0]}"):The Diskprint Workflow has an error in an Ubuntu package, awaiting resolution confirmation.\n\n"
#TODO "${this_script_dir}/diskprint_workflow/deps/install_dependent_packages-ubuntu-14.04.sh"

sudo apt-get --yes install \
  p7zip \
  python-pandas \
  python-pygraphviz \
  python3-pandas \
  python3-psycopg2 \
  python3-seaborn
