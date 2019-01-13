#!/usr/bin/env python
import ephem
import os
import sys
import time
import math

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
    sidt = (hours, minutes, seconds)
    return (sidt)

longy = float(os.getenv("LONGITUDE"))

curst = cur_sidereal(longy)
curst = curst[0]*3600 + curst[1]*60 + curst[2]

dst = sys.argv[1]
dst = dst.split(":")
dst = int(dst[0])*3600 + int(dst[1])*60

ddiff = dst - curst

if (ddiff < 0):
	ddiff = (24*3600) - abs(ddiff)

ltp = time.localtime(time.time()+ddiff)

print ("%02d:%02d" % (ltp.tm_hour, ltp.tm_min))
