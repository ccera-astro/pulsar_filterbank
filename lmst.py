#!/usr/bin/env python
import ephem
import os
import sys


def cur_sidereal(longitude):
    longstr = "%02d" % int(longitude)
    longstr = longstr + ":"
    longitude = abs(longitude)
    frac = longitude - int(longitude)
    frac *= 60
    mins = int(frac)
    longstr += "%02d" % mins
    longstr += ":00"
    x = ephem.Observer()
    x.date = ephem.now()
    x.long = longstr
    jdate = ephem.julian_date(x)
    tokens=str(x.sidereal_time()).split(":")
    hours=int(tokens[0])
    minutes=int(tokens[1])
    seconds=int(float(tokens[2]))
    sidt = float(hours) + float(minutes/60.0) + float(seconds/3600.0)
    return (sidt)

longitude = -76.03
if (len(sys.argv) > 1):
    longitude = float(sys.argv[1])
else:
    if (os.getenv("LONGITUDE") != None):
        longitude = float(os.getenv("LONGITUDE"))

print "%f" % cur_sidereal(longitude)
