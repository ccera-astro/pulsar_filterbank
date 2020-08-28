#!/usr/bin/python2
import os
import sys
#
# Produced with:
#
#   psrcat -c "PSRB PSRJ RAJ DECJ DM W50 P0" -l "S400 > 10" -o short
#
def decimalize(s):
    stoks=s.split(":")
    if (len(stoks) == 1):
        return(float(stoks[0]))
    hours = float(stoks[0])
    minutes = float(stoks[1])
    seconds = float(stoks[1])
    sign = -1.0 if hours < 0.0 else 1
    hours = abs(hours)
    return (sign*(hours+(minutes/60.0)+(seconds/3600.0)))

fp = sys.stdin

lines=fp.readlines()

for line in lines:
    line = line.replace("\n", "")
    toks = line.split()
    if "---" not in line and len(toks) >= 7 and unicode(toks[0]).isnumeric() == True:
       bname=toks[1].lower()
       jname=toks[2].lower()
       if (bname == "*" and jname == "*"):
           continue
       if (toks[3] == "*" or toks[4] == "*"):
           continue
       ra=decimalize(toks[3])
       dec=decimalize(toks[4])
       dm=toks[5]
       if (toks[6] == "*"):
           continue
       pw50=float(toks[6])*1.0e-3
       p0=float(toks[7])
       fmt="NAME=%s; DEC=%-7.3f; RA=%-7.3f; PW50=%-9.6f; DM=%s; P0=%-9.6f"
       if (bname != "*"):
           print fmt % (bname, dec, ra, pw50, dm, p0)
       if (bname != jname):
           if (jname != "*"):
               print fmt % (jname, dec, ra, pw50, dm, p0)
