# this module will be imported in the into your flowgraph
import time
import os
import shutil
import math
import struct
import pmt
import numpy
import random

smpwidth = 0

#
# Determine reasonable decimation value, given sample-rate,
#  filterbank-size (already determined) and pw50 for the
#  target pulsar.
#
# This is not stunningly efficient, but it only has to run
#  ONCE on startup.
#
def determine_rate(srate,fbsize,pw50):
    decims = [1024,512,256,128,64,32,16,8,4,2,1]
    target_rate = (1.0/pw50)
    target_rate *= 10.0
    for d in decims:
        if ((srate/fbsize)/d >= target_rate):
            return d
    return 1

#
# Convert DM to a reasonable number of FFT bins, given
#  DM, center-frequency, bandwidth, and pw50
# 
def dm_to_bins(dm,freq,bw,pw50):
    
    #
    # Convert to milliseconds (sigh)
    #
    p50ms = pw50 * 1000.0
    
    f_lower = (freq-(bw/2.0))*1.0e-6
    f_upper = (freq+(bw/2.0))*1.0e-6
    Dt = 4.15e6 * (math.pow(f_lower,-2.0)-math.pow(f_upper,-2.0))
    Dt *= dm
    
    #
    # So that there's only 5% (of W50) residual smearing in each channel of the FB
    #
    required_bins = Dt/(p50ms/20.0)
    
    #
    # We do a bit of base2 math to make this a nice FFT size
    #
    bins = math.log(required_bins)/math.log(2.0)
    if (abs(bins-int(bins)) > 0.2):
        bins += 1
    
    bins = int(bins)
    
    #
    # No sense making the filterbank too small
    # Set bins so that minimum is 32 channels
    if bins < 5:
        bins = 5

    return(int(2**bins))

#
# Write an external, text, header file
#
def write_header(fn, freq, bw, fbsize, fbrate, smpsize):
    global smpwidth
    
    if (smpwidth == 0):
        smpwidth = smpsize
        
    f = open(fn, "w")
    ltp = time.gmtime(time.time())
    f.write("frequency=%.5f\n" % freq)
    f.write("RF sample rate=%.5f\n" % bw)
    f.write("Filterbank Size=%d\n" % fbsize)
    f.write("Filterbank output rate=%.6f\n" % fbrate)
    f.write("Approx start UTC Date=%04d%02d%02d\n" % (ltp.tm_year,
        ltp.tm_mon, ltp.tm_mday))
    f.write("Approx start UTC Time=%02d:%02d:%02d\n" % (ltp.tm_hour,
        ltp.tm_min, ltp.tm_sec))
    f.write("Output sample size %d bytes\n" % smpsize)
    f.write("Expected disk write rate: %6.2f mbyte/sec\n" % ((fbsize*fbrate*smpsize)/1.0e6))
    


header_args = {}

#
# Convert to the weirdness that is the hybrid floating-point
#  time format used by SIGPROC
#
def convert_sigproct(v):
    itime = int(v*3600.0)
    hours = itime/3600
    minutes = (itime-(hours*3600))/60
    seconds = itime - (hours*3600) - (minutes*60)
    timestr="%02d%02d%02d.0" % (hours, minutes, seconds)
    return(float(timestr))
  
#
# This will cause a header block to be prepended to the output file
#
# Thanks to Guillermo Gancio (ganciogm@gmail.com) for the inspiration
#   and much of the code
#
def build_header_info(outfile,source_name,source_ra,source_dec,freq,bw,fbrate,fbsize,rx_time,smpsize):
    global smpwidth
    
    if (smpwidth == 0):
        smpwidth = smpsize

    header_args["outfile"] = outfile
    header_args["source_name"] = source_name
    header_args["source_ra"] = source_ra
    header_args["source_dec"] = source_dec
    header_args["freq"] = freq
    header_args["bw"] = bw
    header_args["fbrate"] = fbrate
    header_args["fbsize"] = fbsize


    #
    # Time for one sample, in sec
    #
    tsamp=1.0/fbrate
    
    #
    # Frequency offset between channels, in MHz
    #
    f_off=bw/fbsize
    f_off /= 1.0e6
    f_off *= -1
    
    #
    # Highest frequency represented in FB, in MHz
    #
    high_freq = freq+(bw/2.0)
    high_freq  /= 1.0e6
    high_freq -= (f_off/2.0)
    
    #
    # Lowest
    #
    low_freq = freq-(bw/2.0)
    low_freq /= 1.0e6
    low_freq += (f_off/2.0)
    
    #
    # Number of subbands
    #
    sub_bands=fbsize
    
    #
    # Determine MJD from file timestamp
    #
    if (rx_time == None):
        fp = open(outfile, "w")
        t_start = (os.path.getmtime(outfile) / 86400) + 40587
    else:
        fp = open(outfile, "w")
        t_start = rx_time
 
    #
    # The rest here is mostly due to Guillermo Gancio ganciogm@gmail.com
    #
    stx="HEADER_START"
    etx="HEADER_END"
    fp.write(struct.pack('i', len(stx))+stx)
    fp.flush()
    #--
    aux="rawdatafile"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    fp.write(struct.pack('i', len(outfile))+outfile)
    #--
    aux="src_raj"
    aux=struct.pack('i', len(aux))+aux
    source_ra = convert_sigproct(source_ra)
    fp.write(aux)
    aux=struct.pack('d', source_ra)
    fp.write(aux)
    fp.flush()

    #--
    aux="src_dej"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    source_dec= convert_sigproct(source_dec)
    aux=struct.pack('d', source_dec)
    fp.write(aux)
    #--
    aux="az_start"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', 0.0)
    fp.write(aux)
    #--
    aux="za_start"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', 0.0)
    fp.write(aux)
    #--
    aux="tstart"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', float(t_start))
    fp.write(aux)
    #--
    aux="foff"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', f_off)
    fp.write(aux)
    #--
    aux="fch1"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', high_freq)
    fp.write(aux)
    #--
    aux="nchans"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', sub_bands)
    fp.write(aux)
    #--
    aux="data_type"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 1)
    fp.write(aux)
    #--
    aux="ibeam"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 1)
    fp.write(aux)
    #--
    aux="nbits"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', smpsize*8)
    fp.write(aux)
    #--
    aux="tsamp"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('d', tsamp)
    fp.write(aux)
    #--
    aux="nbeams"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 1)
    fp.write(aux)
    #--
    aux="nifs"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 1)
    fp.write(aux)
    #--
    aux="source_name"
    fp.write(struct.pack('i', len(aux))+aux)
    fp.write(struct.pack('i', len(source_name))+source_name)
    #--
    aux="machine_id"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 20)
    fp.write(aux)
    #--
    aux="telescope_id"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
    aux=struct.pack('i', 20)
    fp.write(aux)
    #--
    fp.write(struct.pack('i', len(etx))+etx)
    fp.flush()
    fp.close
    return True

def auto_to_freqs(mask, freq, bw):
    start = freq+(bw/2)
    bins = len(mask)
    decr = bw/bins
    flist = ""
    for i in range(len(mask)):
        if (mask[i] == 0.0):
            flist += "%8.4f," % (start/1.0e6)
        start -= decr
    return flist
#
# We're called fairly frequently, but we only want to log every 10 seconds
#
next_fft = time.time() + 10.0
smooth_fft = [0.0]
fft_cnt = 0
last_smooth = time.time()
def log_fft(freq,bw,prefix,fft):
    global next_fft
    global automask
    global smooth_fft
    global fft_cnt
    global last_smooth
    
    #
    # Degenerate FFT length--sometimes on startup
    #
    if (len(fft) < 2):
        return
    
    #
    # Provide "smooth" FFT for get_correction
    #  function
    #
    if ((time.time() - last_smooth) >= 1.5):
        if (len(smooth_fft) != len(fft)):
            smooth_fft = numpy.array([0.0]*len(fft))
        fft_cnt += 1
        smooth_fft = numpy.add(fft,smooth_fft)
        last_smooth = time.time()
    #
    # Not yet time
    #
    if (time.time() < next_fft):
        return
    
    #
    # Schedule our next one
    #
    next_fft = time.time() + 10.0
 
    #
    # Get current time, break out into "struct tm" style time fields
    #
    ltp = time.gmtime(time.time())
    
    #
    # Constract filename from parts
    #
    date = "%04d%02d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday, ltp.tm_hour)
    fp = open(prefix+date+"-fft.csv", "a")
    
    #
    # Write UTC header
    #
    fp.write("%02d:%02d:%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec))
    
    #
    # Spectrum is inverted:  Fc+bw/2 to Fc-bw/2
    #
    # Required for PRESTO tooling
    # So we start at the high end and work our way backwards
    #
    for i in range(len(fft)-1,-1,-1):
        if (fft[i] <= 0.0):
            fp.write("??,")
        else:
            fp.write("%.2f," % (10.0*math.log10(fft[i]/len(fft))))
    fp.write("\n")
    fp.close()

    mf = open (prefix+date+"-automask.txt", "w")
    mf.write (auto_to_freqs(automask,freq,bw))
    mf.close()



#
# This is called from a 10s-of-Hz poll with a list of "current_tags"
#
# We record the time that the first tag flashes past us.
#
#
# We maintain a static tag dictionary for use later by the header
#  update code
#
tag_dict = {} 
first_tag = None
def process_tag(tags):
    global first_tag
    for tag in tags:
        tag_dict[pmt.to_python(tag.key)] = pmt.to_python(tag.value)
        if (first_tag == None):
            first_tag = time.time()
    
#
# Used to find a tag in the tag_dict
#
def get_tag(key):
    if (key in tag_dict):
        return (tag_dict[key])
    else:
        return None
        
didit = False
#
# Basically, near the end of the run, concatenates the correct header data
#  and the live sample data, and produces a final ".fil" output file.
#
def update_header(pacer,runtime,smpsize):
    global didit
    global first_tag
    import time
    import shutil
    import os
    global smpwidth
    
    if (smpwidth == 0):
        smpwidth = smpsize

    #
    # If we haven't seen our first tag yet, data flow hasn't started
    #
    # The first tag showing up triggers us to record the local time.
    #
    # This allows us to form a rough estimate of when to do the
    #  file-merge, and also, will be our starting timestamp if the
    #  data stream never had an rx_time tag.
    #
    #
    if (runtime != None):
        if (first_tag == None):
            return None
        else:
            endtime = first_tag + runtime
            endtime -= 0.5
    #
    # We're being called as an exit handler
    # 
    else:
        endtime = time.time() - 30.0
        didit = False
    
    #
    # This little dance ensures that we only update the header and concatenate
    #   the live sample data when:
    #
    #   o   We're close to the end of the run
    #   o   We haven't already done this
    #
    if ((time.time() >= endtime) and didit == False):
        
        #
        # We retrieve the previously-cached "rx_time" tag
        #
        # If "none", then we use "first_tag" value
        #
        times = get_tag("rx_time")
        if (times != None):
            seconds = float(times[0])+float(times[1])
        else:
            # 
            # This will result in a very-rough approximation
            #
            if (first_tag != None):
                seconds = first_tag
            else:
                seconds = time.time()
            print "No rx_time tag, start time will be approximate."
        
        #
        # Turn real seconds into MJD
        #
        MJD = seconds/86400.0
        MJD += 40587.0
        build_header_info(header_args["outfile"],
            header_args["source_name"],
            header_args["source_ra"],
            header_args["source_dec"],
            header_args["freq"],
            header_args["bw"],
            header_args["fbrate"],
            header_args["fbsize"],
            MJD,smpsize)
        dataname = header_args["outfile"].replace(".fil", ".filtmp")
        try:
            inf = open(dataname, "r")
            outf = open(header_args["outfile"], "a")
            #
            # Concatenate the live sample data onto the .fil file, which
            #   at this point, only contains the header data
            #
            shutil.copyfileobj(inf, outf)
            inf.close()
            outf.close()
            didit = True
            #
            # We don't need the ".filtmp" file anymore, blow it away
            #
            os.remove(dataname)
        except:
            pass

    return None

def get_swidth():
    return smpwidth

#
# Calculate a "static" RFI mask--basically a vector of either 1.0 or 0.0
#   depending on whether this bin is "in" or excised
#
# Input is an RFI list, as a string, with comma-separated frequency values
#   in Hz.
#
# This mask will get multiplied by the filterbank outputs--so at a position
#   with a "1.0", that filterbank bin will be included, else it won't.
#
def static_mask(freq,bw,fbsize,rfilist):
    
    #
    # If no RFI list, the mask is all 1.0
    #
    if (rfilist == "" or len(rfilist) == 0 or rfilist == None):
        return ([1.0]*fbsize)
    
    #
    # Step size is the bandwidth over the filterbank size
    #   (bin width, basically, in Hz)
    #
    step = bw/fbsize
    start = freq-(bw/2.0)
    end = freq+(bw/2.0)
    
    #
    # Parse the RFI list, do a little sanity checking
    #  on the values.
    #
    rfi = rfilist.split(",")
    mask = [1.0]*fbsize
    for r in rfi:
        try:
            ndx = float(r)-start
            ndx = ndx/step
            ndx = int(ndx)
            if (ndx >= 0 and ndx < len(mask)):
                mask[ndx] = 0.0
        except:
            pass
    mask.reverse()
    return(mask)

#
# Compute a "dynamic mask".  This is part of a two-stage process for
#  implementing spectral-based RFI excision.  The first stage "blanks"
#  the excised channels.  The second stage arranges for the "blanked"
#  channels to have a median estimate +/- a small amount of noise
#  in them.  This is better than a sudden "empty" channel for post-facto
#  folding.
#
# Since this second mask is incorporated by a vector addition operation, the
#  "good" channels will have a 0.0 in the mask, and the "bad" channels
#  will have the locally-estimated mean in them.
#
count=0
deviation=0.0
automask=None
current_estimate=0.0
def dynamic_mask(fft,smask,thresh):
    global count
    global deviation
    global automask
    global current_estimate
   
    
    
    if (automask == None):
        automask = [1.0]*len(fft)
    
    #
    # Our ultimate mask is based on both the user-input static mask
    #  and the dynamically-determined mask
    #
    smask = list(numpy.multiply(smask,automask))
    
    #
    # How many blanked/excised channels in the static mask?
    #
    nzero = smask.count(0.0)
    
    #
    # Determine trim range
    #
    lf = len(fft)
    ff = lf/10
    
    #
    # Calculate mean deviation, but only occasionally
    # Update automask, but only occasionally
    #
    if ((count % 15) == 0):
        #
        # Make "trimmed" versions of mask and input FFT
        #
        trim_fft = fft[ff:-ff]
        trim_mask = list(smask[ff:-ff])
        
        #
        # Compute a quick mean
        # Since the trim_fft bins at the trim_mask excision locations will
        #    be zero, we can use "sum" with confidence
        #
        #
        # The count for the mean will be the length of the input,
        #   minus the number of zeros in the mask
        #
        mcount = len(trim_fft)-trim_mask.count(0.0)
        dmean = sum(numpy.multiply(trim_fft,trim_mask))
        dmean /= mcount
        
        #
        # Now compute average deviation
        #
        adev = 0.0
        for i in range(len(trim_fft)):
            if (trim_mask[i]):
                adev += abs(trim_fft[i]-dmean)
        
        #
        # Automask looks for FFT values that exceed the current
        #  mean estimate by a significant factor--a pulsar will
        #  never do this.  Sporadic narrowband RFI will.
        #
        #
        for i in range(len(fft)):
            
            #
            # Bigger than threshold? It goes on the automask
            #  AND NEVER LEAVES!  This prevents oscillation
            #  over timescales that would be similar to pulsars...
            #
            if (fft[i] > (dmean*thresh)):
                automask[i] = 0.0
        
        #
        # Two-point smoothing on deviation
        #
        if (deviation != 0.0):      
            deviation += adev/mcount
            deviation /= 2.0
        else:
            deviation = adev/mcount

    count +=1

    #
    # Compute the mean
    # First: apply the mask
    #
    # We add up all the non-masked channels
    #
    mean = numpy.multiply(smask,fft)
    mean = mean[ff:-ff]
    lnm = len(mean)
    mean = sum(mean)
    
    #
    # Then: divide by length - count of blanked channels
    #  (divide by count of non-masked channels, IOW)
    #
    mean = mean/float(lnm-nzero)
    mask = [0.0]*len(smask)
    current_estimate = mean
    i = 0
    if False:
        for s in smask:
            
            #
            # We apply the locally-estimated mean, and then dither by a
            #  small amount--this makes sure that the correlation of the
            #  blanked channels tends to be poor.  I hope.
            #
            if (s < 1.0):
                mask[i] = random.uniform(mean-(deviation/2.0),mean+(deviation/2.0))
            i += 1
    
    return(smask)
    
def invert_rfi_mask(mask):
    rmask = []
    for i in range(0,len(mask)):
        rmask.append(1.0 if mask[i] == 0.0 else 0.0)
    return rmask

estithen = time.time()
frozen_estimate = 0.0   
def get_current_estimate():
    global current_estimate
    global frozen_estimate
    
    if (time.time() - estithen < 90):
        frozen_estimate = current_estimate
        return current_estimate
    else:
        return frozen_estimate

#
# Compute passband flatness correction
#
# Use the middle 8 bins as an average to normalize to
#
last_correct = time.time()
correct_state = 0
correction = [0.0]
def get_correction(fbsize,correct,pacer):
    global last_correct
    global smooth_fft
    global fft_cnt
    global correct_state
    global correction

    #
    # They haven't asked for correction
    #
    if (correct == 0):
        return [1.0]*fbsize
    
    #
    # If time to return a correction estimate
    #
    if ((time.time() - last_correct) > 90):
        # Compute correction if we haven't already done so
        if (correct_state == 0):
            correct_state = 1
            
            #
            # Compute the fraction of the buffer we're ignoring
            #  for calculation of the average level
            #
            frac = int(fbsize/6)
            
            #
            # Reduce smooth by fft_cnt
            #
            smooth_fft = numpy.divide(smooth_fft,fft_cnt)
            fft_cnt = 1
            
            #
            # Produce the "window" over which we'll average
            #
            avg_window = smooth_fft[frac:-frac]
            
            #
            # Average that "window"
            #
            avg = sum(avg_window)
            avg /= float(len(avg_window))
            
            
            #
            # Compute the ratio between the average and the smoothed FFT, and
            #  produce a scaling vector that makes them all roughly at the same level
            #
            # We only do thiS ONCE in an entire run near the beginning,
            #   otherwise, other bad things will happen
            #
            # This should be OK, since the *ratios* should remain roughly
            #  the same, even if the baseline noise level changes, due to
            #  background continuum level changes, etc.
            #
            correction = numpy.divide([avg]*fbsize,smooth_fft)
        return correction
    #
    # Not yet time, return no correction
    #
    else:
        return [1.0]*fbsize
    
def get_sky_freq(sky,freq):
    return sky if sky != 0.0 else freq

def autoscale(scale,pace):
    p = get_current_estimate()
    if (p > 1.0e-12):
        return float(scale/p)
    else:
        return 1.0

current_channel = 0
def get_current_channel(pacer,nchan):
    global current_channel
    
    r = [0.0]*nchan
    r[current_channel] = 1.0
    current_channel += 1
    if (current_channel >= nchan):
        current_channel = 0
    return r

channels = None
chcnts = None
spikes = None
lastchan = -1
def analyser(fft,nchan):
    global automask
    global channels
    global chcnts
    global spikes
    global lastchan
    
    nfft = fft[0:len(fft)/2]
    if channels == None:
        channels = [numpy.array([0.0]*len(nfft))]*nchan
        chcnts = [0.0]*nchan
        spikes = [0]*nchan
    
    ccn = current_channel
    channels[ccn] = numpy.add(nfft,channels[ccn])
    chcnts[ccn] += 1.0
    
    #
    # Ignore if this is the first data after a channel change
    #
    if (ccn != lastchan):
        #print "New channel %d" % ccn
        lastchan = ccn
        return ccn
    
    chavg = numpy.divide(channels[ccn], chcnts[ccn])
    
    spike = 0
    winsize = 6
    if (chcnts[ccn] > 10):
        for inspected in range(winsize,len(chavg)-winsize):
            window = sum(chavg[inspected-winsize:inspected-1])
            window /= float(winsize)
            if (chavg[inspected] > window*3.5):
                spike += 1
 
        if (spike == 0):
            if (spikes[ccn] > 0):
                spikes[ccn] -=1

        elif (spike > 1):
            spikes[ccn] += 1

        if (spikes[ccn] > 10):
            automask[ccn] = 0.0

    return ccn

