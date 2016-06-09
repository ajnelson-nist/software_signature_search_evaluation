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

"""
This module provides a function to normalize Registry paths across multiple Windows versions.
"""

__version__ = "0.3.0"

import re
import logging
import os
import functools #For memoization

_logger = logging.getLogger(os.path.basename(__file__))

_PREFIXES_NAGGED = set()

#Key: Normalization prefix (coded in alphabetical order)
NORMALIZED_PREFIXES = {
    #NOTE XP didn't have a components hive.
  "__NORMROOT_COMPONENTS_CONFIG__": re.compile(r"""
    ^
    (
        \\CMI-CreateHive{01805EB9-6A44-4260-806A-28C437337F1F}          #Vista 32-bit
      | \\CMI-CreateHive{1E9602D2-358E-480D-9215-756B81CA7EEB}          #Vista 64-bit
      | \\CMI-CreateHive{0AF462BC-5E78-4490-BC7A-5FF5DE05A8F0}          #7 32-bit
      | \\CMI-CreateHive{D9D79F5E-5CCC-4BEF-BA86-8462C417D5BE}          #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}     #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE XP did not contribute any NtUser config hives.
  "__NORMROOT_NTUSER_CONFIG__": re.compile(r"""
    ^
    (
        \\{bf1a281b-ad7b-4476-ac95-f47682990ce7}C:/WINDOWS/System32/config/systemprofile/ntuser.dat    #Vista and 8, 32-bit and 64-bit
      | \\{bf1a281b-ad7b-4476-ac95-f47682990ce7}X:/WINDOWS/System32/config/systemprofile/ntuser.dat    #7, 32-bit and 64-bit
    )
    (.*)                                                                                               #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_NTUSER_DEFAULT__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{B01E557D-7818-4BA7-9885-E6592398B44E}        #Vista 32-bit
      | \\CMI-CreateHive{D9E7ECFE-4384-424F-8CCD-D73E8D171A4B}        #Vista 64-bit
      | \\CMI-CreateHive{6A1C4018-979D-4291-A7DC-7AED1C75B67C}        #7 32-bit
      | \\CMI-CreateHive{D43B12B8-09B5-40DB-B4F6-F6DFEB78DAEC}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_NTUSER_LOCALSERVICE__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{B01E557D-7818-4BA7-9885-E6592398B44E}        #Vista 32-bit
      | \\CMI-CreateHive{D9E7ECFE-4384-424F-8CCD-D73E8D171A4B}        #Vista 64-bit
      | \\CMI-CreateHive{6A1C4018-979D-4291-A7DC-7AED1C75B67C}        #7 32-bit
      | \\CMI-CreateHive{D43B12B8-09B5-40DB-B4F6-F6DFEB78DAEC}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_NTUSER_NETWORKSERVICE__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{B01E557D-7818-4BA7-9885-E6592398B44E}        #Vista 32-bit
      | \\CMI-CreateHive{D9E7ECFE-4384-424F-8CCD-D73E8D171A4B}        #Vista 64-bit
      | \\CMI-CreateHive{6A1C4018-979D-4291-A7DC-7AED1C75B67C}        #7 32-bit
      | \\CMI-CreateHive{D43B12B8-09B5-40DB-B4F6-F6DFEB78DAEC}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive only appears in XP.
  "__NORMROOT_NTUSER_REPAIR__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_NTUSER_USER__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{B01E557D-7818-4BA7-9885-E6592398B44E}        #Vista 32-bit
      | \\CMI-CreateHive{D9E7ECFE-4384-424F-8CCD-D73E8D171A4B}        #Vista 64-bit
      | \\CMI-CreateHive{6A1C4018-979D-4291-A7DC-7AED1C75B67C}        #7 32-bit
      | \\CMI-CreateHive{D43B12B8-09B5-40DB-B4F6-F6DFEB78DAEC}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_SAM_CONFIG__": re.compile(r"""
    ^
    (
      \\SAM                                                           #XP
      | \\CMI-CreateHive{87E016C8-C811-4B12-9C3A-CDA552F3458D}        #Vista 32-bit
      | \\CMI-CreateHive{09F2A9C3-63AA-4100-A549-76217DBD1AA6}        #Vista 64-bit
      | \\CMI-CreateHive{899121E8-11D8-44B6-ACEB-301713D5ED8C}        #7 32-bit
      | \\CMI-CreateHive{C4E7BA2B-68E8-499C-B1A1-371AC8D717C7}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive only appears in XP.
  "__NORMROOT_SAM_REPAIR__": re.compile(r"""
    ^
    (
      \\SAM                                                           #XP
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_SECURITY_CONFIG__": re.compile(r"""
    ^
    (
      \\SECURITY                                                      #XP
      | \\CMI-CreateHive{AA22D55B-E3D8-431D-A6EC-AACEF8D4F3B3}        #Vista 32-bit
      | \\CMI-CreateHive{FC24C862-A844-46D6-87E7-FECC00251085}        #Vista 64-bit
      | \\CMI-CreateHive{FE0DCB88-9AD4-44DC-AED8-DCE1C037E9E5}        #7 32-bit
      | \\CMI-CreateHive{0297523D-E529-4E42-8BE7-E1AABC063C84}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive only appears in XP.
  "__NORMROOT_SECURITY_REPAIR__": re.compile(r"""
    ^
    (
      \\SECURITY                                                      #XP
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive only appears in XP.
  "__NORMROOT_SOFTWARE_REPAIR__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_SOFTWARE_CONFIG__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{29EE1162-53C9-4474-A2B6-D90A7F6B0A7C}        #Vista 32-bit
      | \\CMI-CreateHive{BF742E91-C1C9-4678-82D3-EE8EEDEC3796}        #Vista 64-bit
      | \\CMI-CreateHive{3D971F19-49AB-4000-8D39-A6D9C673D809}        #7 32-bit
      | \\CMI-CreateHive{199DAFC2-6F16-4946-BF90-5A3FC3A60902}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_SYSTEM_CONFIG__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
      | \\CMI-CreateHive{C619BFE8-791A-4B77-922B-F114AB570920}        #Vista 32-bit
      | \\CMI-CreateHive{3406549D-D5AD-434A-9894-E927ABEC8146}        #Vista 64-bit
      | \\CMI-CreateHive{F10156BE-0E87-4EFB-969E-5DA29D131144}        #7 32-bit
      | \\CMI-CreateHive{2A7FB991-7BBE-4F9D-B91E-7CB51D4737F5}        #7 64-bit
      | \\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}   #8 32-bit, 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive only appears in XP.
  "__NORMROOT_SYSTEM_REPAIR__": re.compile(r"""
    ^
    (
      \\\$\$\$PROTO.HIV                                               #XP
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive does not appear in Vista 32-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in Vista 64-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 7 32-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 7 64-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 8 64-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).  However, once an appwas installed on 8 32-bit, the hive appeared.  It may appear in the future, hopefully under the same name.
  "__NORMROOT_USRCLASS_LOCALSERVICE__": re.compile(r"""
    ^
    (
        \\S-1-5-19_Classes                                            #XP
      | \\User-1_Classes                                              #8 32-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  #NOTE This hive does not appear in Vista 32-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in Vista 64-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 7 32-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 7 64-bit (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).
  #NOTE This hive does not appear in 8 64-bit *baseline prints* (UsrClass.dat only appears once as a basename in the whole fiout.dfxml).  However, once an appwas installed on 8 32-bit, the hive appeared.  It may appear in the future, hopefully under the same name.
  "__NORMROOT_USRCLASS_NETWORKSERVICE__": re.compile(r"""
    ^
    (
        \\S-1-5-20_Classes                                              #XP
      | \\User-2_Classes                                                #8 32-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE),

  "__NORMROOT_USRCLASS_USER__": re.compile(r"""
    ^
    (
      \\S-[-0-9]+_Classes                                             #XP, Vista 32-bit, Vista 64-bit, 7 32-bit, 7 64-bit, 8 32-bit, 8 64-bit
    )
    (.*)                                                              #Rest of string
  """, re.VERBOSE)
}

RX_EXTRACT_PREFIX = re.compile(r"""
  ^\\[^\\]+
""", re.VERBOSE)

def extract_prefix(path):
    the_match = RX_EXTRACT_PREFIX.match(path)
    if the_match is None:
        return None
    return the_match.group()

@functools.lru_cache(maxsize=128)
def hive_path_to_prefix(hive_path):
    """
    @hive_path: The file system path from the hive's originating disk image.
    @cell_path: Path of the cell within the hive.
    """
    norm_prefix = None
    rx = None

    known_paths_to_prefixes = {
      "Documents and Settings/Default User/NTUSER.DAT"                                                      : "__NORMROOT_NTUSER_DEFAULT__",
      "Documents and Settings/LocalService/Local Settings/Application Data/Microsoft/Windows/UsrClass.dat"  : "__NORMROOT_USRCLASS_LOCALSERVICE__",
      "Documents and Settings/LocalService/NTUSER.DAT"                                                      : "__NORMROOT_NTUSER_LOCALSERVICE__",
      "Documents and Settings/NetworkService/Local Settings/Application Data/Microsoft/Windows/UsrClass.dat": "__NORMROOT_USRCLASS_NETWORKSERVICE__",
      "Documents and Settings/NetworkService/NTUSER.DAT"                                                    : "__NORMROOT_NTUSER_NETWORKSERVICE__",
      "Users/Default/NTUSER.DAT"                                                                            : "__NORMROOT_NTUSER_DEFAULT__",
      "WINDOWS/repair/ntuser.dat"                                                                           : "__NORMROOT_NTUSER_REPAIR__",
      "WINDOWS/repair/sam"                                                                                  : "__NORMROOT_SAM_REPAIR__",
      "WINDOWS/repair/security"                                                                             : "__NORMROOT_SECURITY_REPAIR__",
      "WINDOWS/repair/software"                                                                             : "__NORMROOT_SOFTWARE_REPAIR__",
      "WINDOWS/repair/system"                                                                               : "__NORMROOT_SYSTEM_REPAIR__",
      "WINDOWS/system32/config/SAM"                                                                         : "__NORMROOT_SAM_CONFIG__",
      "WINDOWS/system32/config/SECURITY"                                                                    : "__NORMROOT_SECURITY_CONFIG__",
      "WINDOWS/system32/config/software"                                                                    : "__NORMROOT_SOFTWARE_CONFIG__",
      "WINDOWS/system32/config/system"                                                                      : "__NORMROOT_SYSTEM_CONFIG__",
      "Windows/ServiceProfiles/LocalService/AppData/Local/Microsoft/Windows/UsrClass.dat"                   : "__NORMROOT_USRCLASS_LOCALSERVICE__",
      "Windows/ServiceProfiles/LocalService/NTUSER.DAT"                                                     : "__NORMROOT_NTUSER_LOCALSERVICE__",
      "Windows/ServiceProfiles/NetworkService/AppData/Local/Microsoft/Windows/UsrClass.dat"                 : "__NORMROOT_USRCLASS_NETWORKSERVICE__",
      "Windows/ServiceProfiles/NetworkService/NTUSER.DAT"                                                   : "__NORMROOT_NTUSER_NETWORKSERVICE__",
      "Windows/System32/config/systemprofile/ntuser.dat"                                                    : "__NORMROOT_NTUSER_CONFIG__",
      "Windows/System32/config/COMPONENTS"                                                                  : "__NORMROOT_COMPONENTS_CONFIG__",
      "Windows/System32/config/SAM"                                                                         : "__NORMROOT_SAM_CONFIG__",
      "Windows/System32/config/SECURITY"                                                                    : "__NORMROOT_SECURITY_CONFIG__",
      "Windows/System32/config/SOFTWARE"                                                                    : "__NORMROOT_SOFTWARE_CONFIG__",
      "Windows/System32/config/SYSTEM"                                                                      : "__NORMROOT_SYSTEM_CONFIG__",
    }
    norm_prefix = known_paths_to_prefixes.get(hive_path)

    if norm_prefix is None:
        if hive_path.endswith("NTUSER.DAT"):
            if hive_path.startswith(("Documents and Settings", "Users")):
                norm_prefix = "__NORMROOT_NTUSER_USER__"
            else:
                raise ValueError("Unexpected hive path with suffix 'NTUSER.DAT': %r." % hive_path)
        elif hive_path.endswith("UsrClass.dat"):
            if hive_path.startswith(("Documents and Settings", "Users")):
                norm_prefix = "__NORMROOT_USRCLASS_USER__"
            else:
                raise ValueError("Unexpected hive path with suffix 'UsrClass.dat': %r." % hive_path)

    if norm_prefix is None:
        _logger.warning("Could not identify the type of this hive by file path: %r." % hive_path)

    return norm_prefix

def normalize_path(hive_path, cell_path):
    global _PREFIXES_NAGGED
    norm_prefix = hive_path_to_prefix(hive_path)
    rx = NORMALIZED_PREFIXES[norm_prefix]
    if rx.match(cell_path):
        return rx.sub(norm_prefix+ r"\2", cell_path)
    
    notnorm_prefix = extract_prefix(cell_path)
    if not notnorm_prefix in _PREFIXES_NAGGED:
        _logger.info("Containing hive path: %r." % hive_path)
        raise ValueError("Could not normalize a cell path: %r." % cell_path)
    return cell_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    for x in [
      r"\$$$PROTO.HIV\ControlSet001\Control\Windows\ShutdownTime",
      r"\CMI-CreateHive{C619BFE8-791A-4B77-922B-F114AB570920}\ControlSet001\Control\Windows\ShutdownTime",
      r"\CMI-CreateHive{3406549D-D5AD-434A-9894-E927ABEC8146}\ControlSet001\Control\Windows\ShutdownTime",
      r"\CMI-CreateHive{F10156BE-0E87-4EFB-969E-5DA29D131144}\ControlSet001\Control\Windows\ShutdownTime",
      r"\CMI-CreateHive{2A7FB991-7BBE-4F9D-B91E-7CB51D4737F5}\ControlSet001\Control\Windows\ShutdownTime",
      r"\CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}\ControlSet001\Control\Windows\ShutdownTime"
    ]:
        if normalize_path("Windows/System32/config/SYSTEM", x) != r"__NORMROOT_SYSTEM_CONFIG__\ControlSet001\Control\Windows\ShutdownTime":
            raise ValueError("Failed to normalize this path: %r." % x)
        x_sans_suffix = x.replace(r"\ControlSet001\Control\Windows\ShutdownTime","")
        if extract_prefix(x) != x_sans_suffix:
            _logger.info("extract_prefix(x) = %r." % extract_prefix(x))
            _logger.info("x_sans_suffix = %r." % x_sans_suffix)
            raise ValueError("Failed to extract prefix: %r." % x)
    assert extract_prefix("\\$$$PROTO.HIV") == r"\$$$PROTO.HIV"
    assert extract_prefix("\\$$$PROTO.HIV\\") == r"\$$$PROTO.HIV"
    assert extract_prefix("\\$$$PROTO.HIV\\asdf\\fdsa") == r"\$$$PROTO.HIV"
