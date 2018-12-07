# this module will be imported in the into your flowgraph
import time

#
# Determine FBSIZE and FBRATE given input sample rate
#
# This is not stunningly efficient, but it only has to run
#  ONCE on startup.
#
def determine_rate(srate):
    if (srate > 6.0e6):
        fbsize_2N = [128,64,32]
        fbsize_10N = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30]
        fbsize_3N = [96, 81, 78, 72, 56, 48, 36]
    else:
        fbsize_2N = [64,32]
        fbsize_10N = [50,45,40,35,30,25]
        fbsize_3N = [72, 56, 48, 36]

    for n in fbsize_2N:
        r = rate_core(srate, n)
        if r > 0:
            return((n,r))
    for n in fbsize_10N:
        r = rate_core(srate, n)
        if r > 0:
            return((n,r))
    for n in fbsize_3N:
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
    for i in range(1800,4800,2):
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
    

