# this module will be imported in the into your flowgraph
import time

#
# Determine FBSIZE and FBRATE given input sample rate
#
# This is not stunningly efficient, but it only has to run
#  ONCE on startup.
#
def determine_rate(srate,fbsize):
	decims = [32,16,8,4,2]
	for d in decims:
		if ((srate/fbsize)/d >= 1250.0):
			return d

#
# Write an external, text, header file
#
def write_header(fn, freq, bw, fbsize, fbrate):
    f = open(fn, "w")
    ltp = time.gmtime(time.time())
    f.write("frequency=%.5f\n" % freq)
    f.write("RF sample rate=%.5f\n" % bw)
    f.write("Filterbank Size=%d\n" % fbsize)
    f.write("Filterbank output rate=%.3f\n" % fbrate)
    f.write("Approx start UTC Date=%04d%02d%02d\n" % (ltp.tm_year,
        ltp.tm_mon, ltp.tm_mday))
    f.write("Approx start UTC Time=%02d:%02d:%02d\n" % (ltp.tm_hour,
        ltp.tm_min, ltp.tm_sec))
    f.write("Expected disk write rate: %6.2f mbyte/sec\n" % ((fbsize*fbrate*2.0)/1.0e6))
    
def synched(startt,dummy):
    
    if (time.time() > startt):
        return True
    else:
        return False

import os
import struct
#
# This will cause a header block to be prepended to the output file
#
# Thanks to Guillermo Gancio (ganciogm@gmail.com) for the inspiration
#   and much of the code
#
def build_header_info(outfile,source_name,source_ra,source_dec,freq,bw,fbrate,fbsize):

	#
	# Time for one sample, in sec
	#
    tsamp=1.0/fbrate
    
    #
    # Frequency offset between channels, in MHz
    #
    f_off=bw/fbsize
    f_off /= 1.0e6
    f_off = -1.0 * f_off
    
    #
    # Highest frequency represented in FB, in MHz
    #
    high_freq = freq+(bw/2.0)
    high_freq  /= 1.0e6
    
    #
    # Number of subbands
    #
    sub_bands=fbsize
    
    #
    # Determine MJD from file timestamp
    #
    fp = open(outfile, "w")
    t_start = (os.path.getmtime(outfile) / 86400) + 40587
    
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

