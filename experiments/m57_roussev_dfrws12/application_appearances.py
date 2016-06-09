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

"""All application notes are derived only from Roussev and Quates, DFRWS 2012; and from file system inspection."""

#Key: Signature document.  Should be named as a diskprint-trained signature document; "m57"-prefixed names are placeholders.
#Value: Dictionary.
#  Key: M57 machine name.
#  Value:  Pair, starting image where signature should match, last image where signature should match (null indicating no software removal).
appearances = {
  #"m57-xp32-7zip/Close"
  "234-1/15233-1/Close": {
    #Source: Page S68, inferred execution.
    "charlie": ("charlie-2009-11-24", None)
  },

  #ETID: 15233-1, version "9.2".
  #Version in Charlie: 4.65, .exe timestamped 2009-02-03.
  #"m57-xp32-7zip/Install"
  "234-1/15233-1/Install": {
    #Source: Page S68.
    "charlie": ("charlie-2009-11-24", None)
  },

  # Version in Pat looks like version "9.0", either Reader or Acrobat Reader (if there's a difference).  ETIDs in app label database: 9703-1, 10748-1, of version 9.3, apparently 2010.
  # Printed version: 2396-1, Adobe Acrobe Reader 3.0, 1995-1996.
  "m57-xp32-adobereader/Close": {
    #Source: Page S67, inferred execution.
    "pat": ("pat-2009-11-19", None)
  },

  "m57-xp32-adobereader/Install": {
    #Actual application installed: Acrobat Reader 9.
    #Source: Page S67.
    "pat": ("pat-2009-11-19", None)
  },

  "m57-xp32-avg/Close": {
    #Source: Page S67, inferred execution ("AVG has been updated.").
    "pat": ("pat-2009-12-03", None)
  },

  #To identify the version, I downloaded port p5-image-exiftool, per advice from <http://unix.stackexchange.com/a/86151>.
  #  But, can't find 'brother.dll' on Pat machine 2009-11-30.  Found a file BRMD05A.EXE, and a bunch of DLLs in a folder named according to a Brother printer model.
  #"m57-xp32-brotherprinterdriver/Install"
  "234-1/17032-1/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-11-30", None)
  },

  "m57-xp32-cygnushexeditor/Close": {
    #Source: Page S68, inferred execution.
    "charlie": ("charlie-2009-11-24", None)
  },

  "m57-xp32-cygnushexeditor/Install": {
    #Source: Page S68.
    "charlie": ("charlie-2009-11-24", None)
  },

  #Firefox
  #Specific version: 3.5.5
  #3.5.5 is NOT in the NSRL.  The closest are:
  #sqlite> SELECT * FROM etid_to_productname WHERE LOWER(productname) LIKE '%irefox%';
  #[snip]
  #7895-2|mozilla Firefox 2|Copyright 2004-2007
  #9620-1|Firefox 3.6|3.6.3
  #[snip]
  #However, we've printed so many, this is probably fine.

  #Source: Page S67, inferred execution.
  #Updated source: Inspection of the file system.
  "8504-1/7895-1/Close": {
    "pat": ("pat-2009-11-12", None)
  },
  "8504-2/7895-1/Close": {
    "pat": ("pat-2009-11-12", None)
  },

  #Source: Page S67.
  "8504-1/7895-1/Install": {
    "pat": ("pat-2009-11-12", None)
  },
  "8504-2/7895-1/Install": {
    "pat": ("pat-2009-11-12", None)
  },

  #m57-xp32-invisiblesecrets
  "234-1/15489-1/Close": {
    #Source: Page S68.
    #TODO A definite lower bound can be established by the creation time of the file microscope1.jpg.
    "charlie": ("charlie-2009-11-19", None)
  },

  #m57-xp32-invisiblesecrets
  "234-1/15489-1/Install": {
    #Source: Page S68 notes appearance of insecr2.exe on Nov. 19.
    "charlie": ("charlie-2009-11-19", None)
  },

  #Specific versions:
  #File Version: 6.0.170.4
  #Full Version: 1.6.0_17-b04
  #Product Name: Java(TM) Platform SE 6 U17
  #Product Version: 6.0.170.4
  #
  #File actually found in starting image.
  #
  "m57-xp32-java/Close": {
    #Source: Page S67, inferred execution.
    "pat": ("pat-2009-11-16", None)
  },

  "m57-xp32-java/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-11-16", None)
  },

  "m57-xp32-mdd/Close": {
    #Source: Page S67, inferred execution.
    "pat": ("pat-2009-11-16", None)
  },

  "m57-xp32-mdd/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-11-16", None)
  },

  #m57-xp32-python
  "234-1/15487-1/Close": {
    #Source: Page S67, inferred execution.
    #Updated source: Inspection of the file system.
    "pat": ("pat-2009-11-12start", None)
  },

  #m57-xp32-python
  "234-1/15487-1/Install": {
    #Source: Page S67.
    #Updated source: Inspection of the file system.
    "pat": ("pat-2009-11-12start", None)
  },

  "m57-xp32-realvncvnc4/Close": {
    #Source: Page S67, inferred execution.
    "pat": ("pat-2009-12-07", None)
  },

  "m57-xp32-realvncvnc4/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-12-07", None)
  },

  #m57-xp32-truecrypt
  "234-1/15488-1/Close": {
    #Source: Figure 1 and Page S67.
    "jo-newComputer": ("jo-2009-12-03", None)
  },

  #m57-xp32-truecrypt
  "234-1/15488-1/Install": {
    #Source: Figure 1 and Page S67.
    "jo-newComputer": ("jo-2009-12-03", None)
  },

  "m57-xp32-win32dd/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-12-07", None)
  },

  #m57-xp32-xpadvancedkeylogger
  "234-1/15485-1/Close": {
    #Source: Page S67, inferred execution.
    "pat": ("pat-2009-12-03", "pat-2009-12-07")
  },

  #m57-xp32-xpadvancedkeylogger
  "234-1/15485-1/Install": {
    #Source: Page S67.
    "pat": ("pat-2009-12-03", "pat-2009-12-07")
  },
}
