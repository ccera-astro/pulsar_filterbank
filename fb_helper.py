# this module will be imported in the into your flowgraph

def determine_rate(srate, fbsize):
    bankrate = float(srate)/float(fbsize)
    for i in range(2500,17000):
        frate = bankrate/float(i)
        irate = float(int(frate))
        if (frate == irate):
            return int(bankrate/irate)
    raise ValueError("No suitable filterbank sample rate could be determined--try different FB size")
