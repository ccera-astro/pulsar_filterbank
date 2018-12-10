# this module will be imported in the into your flowgraph
import time

#
# Determine FBSIZE and FBRATE given input sample rate
#
# This is not stunningly efficient, but it only has to run
#  ONCE on startup.
#
def determine_rate(srate):
    fbsize_2N = [192,160,128,96,64,48,32,100,50,25]
    for n in fbsize_2N:
        r = rate_core(srate, n)
        if r > 0:
            return((n,r))

    raise RuntimeError("Unable to determine useful FBSIZE/FBRATE combination given sample rate")

#
# Given sample rate, and fbsize, determine a useful rate
#  Return -1 if no rate could be determined
#
def rate_core(srate, fbsize):
    bankrate = float(srate)/float(fbsize)
    for i in range(1800,5600):
        frate = bankrate/float(i)
        irate = float(int(frate))
        if (frate == irate):
            return int(bankrate/irate)
    return -1

def write_header(fn, freq, bw, fbsize, fbrate):
    f = open(fn, "w")
    ltp = time.gmtime(time.time())
    f.write("frequency=%.5f\n" % freq)
    f.write("RF sample rate=%.5f\n" % bw)
    f.write("Filterbank Size=%d\n" % fbsize)
    f.write("Filterbank output rate=%d\n" % fbrate)
    f.write("Approx start UTC Date=%04d%02d%02d\n" % (ltp.tm_year,
        ltp.tm_mon, ltp.tm_mday))
    f.write("Approx start UTC Time=%02d:%02d:%02d\n" % (ltp.tm_hour,
        ltp.tm_min, ltp.tm_sec))
    

def synched(startt,dummy):
    if (time.time() > startt):
        return True
    else:
        return False
