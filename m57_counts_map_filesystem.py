#!/usr/bin/env python3.3

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

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import Objects

def main():
    global args

    #Count allocated files from file system
    fs_count = 0
    _logger.debug("Begin iterparse of %r." % args.fiout_dfxml)
    for (event, obj) in Objects.iterparse(args.fiout_dfxml):
        if not isinstance(obj, Objects.FileObject):
            continue
        if not obj.is_allocated():
            continue
        fs_count += 1

    with open(args.text_output, "w") as fh:
        fh.write(str(fs_count))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("fiout_dfxml")
    parser.add_argument("text_output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
