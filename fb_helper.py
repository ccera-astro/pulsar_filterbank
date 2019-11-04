# this module will be imported in the into your flowgraph
import time
import os
import shutil

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
def write_header(fn, freq, bw, fbsize, fbrate):
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
    f.write("Expected disk write rate: %6.2f mbyte/sec\n" % ((fbsize*fbrate*2.0)/1.0e6))
    

import os
import struct
header_args = {}
#
# This will cause a header block to be prepended to the output file
#
# Thanks to Guillermo Gancio (ganciogm@gmail.com) for the inspiration
#   and much of the code
#
def build_header_info(outfile,source_name,source_ra,source_dec,freq,bw,fbrate,fbsize,rx_time):

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
    fp.write(aux)
    aux=struct.pack('d', source_ra)
    fp.write(aux)
    fp.flush()

    #--
    aux="src_dej"
    aux=struct.pack('i', len(aux))+aux
    fp.write(aux)
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
    aux=struct.pack('i', 16)
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

import math

def log_fft(freq,bw,prefix,fft):
    
    if (len(fft) < 2):
        return
    
    ltp = time.gmtime(time.time())
    date = "%04d%02d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday, ltp.tm_hour)
    fp = open(prefix+date+"-fft.csv", "a")
    
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



import pmt
tag_dict = {} 
first_tag = None
def process_tag(tags):
    global first_tag
    for tag in tags:
        tag_dict[pmt.to_python(tag.key)] = pmt.to_python(tag.value)
        if (first_tag == None):
            first_tag = time.time()
    

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
def update_header(pacer,runtime):
    global didit
    global first_tag
    import time
    import shutil
    import os

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
            MJD)
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

