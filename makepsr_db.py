#!/usr/bin/python2
import os
import sys
def decimalize(s):
	stoks=s.split(":")
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
    if len(toks) == 12 and unicode(toks[0]).isnumeric() == True:
       bname=toks[1].lower()
       jname=toks[2].lower()
       ra=decimalize(toks[3])
       dec=decimalize(toks[4])
       dm=toks[7]
       pw50=float(toks[8])*1.0e-3
       fmt="NAME=%s; DEC=%-7.3f; RA=%-7.3f; PW50=%-9.6f; DM=%s"
       print fmt % (bname, dec, ra, pw50, dm)
       if (bname != jname):
		   print fmt % (jname, dec, ra, pw50, dm)
