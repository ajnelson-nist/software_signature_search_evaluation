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

MACHINE_TAG_SEQUENCES = {
  "charlie": [
    "charlie-2009-11-12start",
    "charlie-2009-11-12",
    "charlie-2009-11-16",
    "charlie-2009-11-17",
    "charlie-2009-11-18",
    "charlie-2009-11-19",
    "charlie-2009-11-20",
    "charlie-2009-11-23",
    "charlie-2009-11-24",
    "charlie-2009-11-30",
    "charlie-2009-12-01",
    "charlie-2009-12-02",
    "charlie-2009-12-03",
    "charlie-2009-12-04",
    "charlie-2009-12-07",
    "charlie-2009-12-08",
    "charlie-2009-12-09",
    "charlie-2009-12-10",
    "charlie-2009-12-11"
  ],
  "jo-oldComputer": [
    "jo-2009-11-12start",
    "jo-2009-11-12",
    "jo-2009-11-16",
    "jo-2009-11-17",
    "jo-2009-11-18",
    "jo-2009-11-19",
    "jo-2009-11-20-oldComputer"
  ],
  "jo-newComputer": [
    "jo-2009-11-20-newComputer",
    "jo-2009-11-23",
    "jo-2009-11-24",
    "jo-2009-11-30",
    "jo-2009-12-01",
    "jo-2009-12-02",
    "jo-2009-12-03",
    "jo-2009-12-04",
    "jo-2009-12-07",
    "jo-2009-12-08",
    "jo-2009-12-09",
    "jo-2009-12-10",
    "jo-2009-12-11-001",
    "jo-2009-12-11-002"
  ],
  "pat": [
    "pat-2009-11-12start",
    "pat-2009-11-12",
    "pat-2009-11-16",
    "pat-2009-11-17",
    "pat-2009-11-18",
    "pat-2009-11-19",
    "pat-2009-11-20",
    "pat-2009-11-23",
    "pat-2009-11-24",
    "pat-2009-11-30",
    "pat-2009-12-01",
    "pat-2009-12-02",
    "pat-2009-12-03",
    "pat-2009-12-04",
    "pat-2009-12-07",
    "pat-2009-12-08",
    "pat-2009-12-09",
    "pat-2009-12-10",
    "pat-2009-12-11"
  ],
  "terry-smallDrive": [
    "terry-2009-11-12start",
    "terry-2009-11-12",
    "terry-2009-11-16",
    "terry-2009-11-17",
    "terry-2009-11-18"
  ],
  "terry-bigDrive": [
    "terry-2009-11-19",
    "terry-2009-11-20",
    "terry-2009-11-23",
    "terry-2009-11-24",
    "terry-2009-11-30",
    "terry-2009-12-01",
    "terry-2009-12-02",
    "terry-2009-12-03",
    "terry-2009-12-04",
    "terry-2009-12-07",
    "terry-2009-12-08",
    "terry-2009-12-09",
    "terry-2009-12-10",
    "terry-2009-12-11-001",
    "terry-2009-12-11-002"
  ]
}

def main():
    with open(args.out_file, "w") as fh:
        for node_id in MACHINE_TAG_SEQUENCES[args.sequence]:
            print(node_id, file=fh)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence", choices=sorted(MACHINE_TAG_SEQUENCES.keys()))
    parser.add_argument("out_file")
    args = parser.parse_args()
    main()
