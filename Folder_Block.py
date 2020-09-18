"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import time


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """A pulsar folder/de-dispersion block"""

    def __init__(self, fbsize=16,smear=10.0,period=0.714,filename='/dev/null',fbrate=2500,tbins=250,interval=30):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Pulsar Folder',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        
        self.set_output_multiple(fbsize)
        self.delaymap = [0]*fbsize
        delayincr = (smear/1000.0) * float(fbrate)
        delayincr /= float(fbsize)
        delayincr = round(delayincr)
        delayincr = int(delayincr)
        for i in range(fbsize):
            self.delaymap[i] = (fbsize-i)*delayincr
        
        self.fbuf = [0.0]*fbsize
        self.flen = len(self.fbuf)
        
        #
        # The pulsar period
        #
        self.p0 = period
        
        #
        # The derived single-period pulse profile
        #
        self.profile = np.array([0.0]*tbins)
        self.pcounts = np.array([0]*len(self.profile))
        
        #
        # Sample period
        #
        self.sper = 1.0/fbrate
        
        #
        # Mission Elapsed Time
        # This is moved along at every time samples arrival--incremented
        #   by 'self.sper'
        #
        self.MET = 0.0
        
        #
        # How much time is in each bin?
        # The profile should be "exactly" as long as a single
        #   pulse period
        #
        self.tbin = self.p0/len(self.profile)
        
        #
        # Open the output file
        #
        self.fname = filename
        
        #
        # The logging interval
        #
        self.INTERVAL = fbrate*interval
        self.logcount = self.INTERVAL
        
        print "sper %f tbin %f ratio %f" % (self.sper, self.tbin, self.tbin/self.sper)
        
    def work(self, input_items, output_items):
        """Do dedispersion/folding"""
        q = input_items[0]
        for i in range(len(q)/self.flen):
            #
            # Do delay/dedispersion logic
            #
            if (self.delaymap[0] > 0):
                outval = 0.0
                for j in range(self.flen):
                    if (self.delaymap[j] == 0):
                        outval += q[(i*self.flen)+j]
                #
                # Decrement delay counters
                #
                for j in range(self.flen):
                    if (self.delaymap[j] > 0):
                        self.delaymap[j] -= 1
                    else:
                        break
            else:
                outval = sum(q[(i*self.flen):(i*self.flen)+self.flen])
            
            #
            # Figure out where this sample goes in the profile buffer, based on MET
            # We place the next sample based on the MET, re-expressed in terms of
            #   total time-bins (self.tbin) modulo the profile length
            #
            where = self.MET/self.tbin
            where = int(where) % len(self.profile)
            
            #
            # Update value in that profile bin
            #
            self.profile[where] += outval
            self.pcounts[where] += 1
            
            #
            # Increment Mission Elapsed Time
            #
            self.MET += self.sper
            
            #
            # Decrement the log counter
            #
            self.logcount -= 1
            
            #
            # If time to log, the output is the reduced-by-counts
            #  value of the profile.
            #
            if (self.logcount <= 0):
                fp = open(self.fname, "w")
                output = np.divide(self.profile,self.pcounts)
                for v in output:
                    fp.write("%-11.7f\n" % v)
                fp.close()
                self.logcount = self.INTERVAL
            
            
        return len(q)
