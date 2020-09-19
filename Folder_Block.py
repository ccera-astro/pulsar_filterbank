"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import time
import json

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
            self.delaymap[(fbsize-i)-1] = i*delayincr
        
        #
        # Needed in a few places
        #
        self.flen = fbsize
        
        #
        # The pulsar period
        #
        self.p0 = period
        
        #
        # The derived single-period pulse profile with various shifts
        #
        #
        self.shifts = [-100.0e-6, -10.0e-6, -5.0e-6, 0.0, 5.0e-6, 10.0e-6, 100.0e-6]
        self.profiles = [[0.0]*tbins]*len(self.shifts)
        self.pcounts = [[0.0]*tbins]*len(self.shifts)
        
        #
        #
        # How much time is in each bin?
        # The profile should be "exactly" as long as a single
        #   pulse period
        #
        self.tbint = []
        for shift in self.shifts:
            self.tbint.append((self.p0*(1.0+shift))/tbins)
        
        #
        # The profile length
        #   
        self.plen = tbins
        
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
        # Open the output file
        #
        self.fname = filename
        self.sequence = 0
        
        self.max_in = 0.0
        self.min_in = 100000000
        
        #
        # The logging interval
        #
        self.INTERVAL = fbrate*interval
        self.logcount = self.INTERVAL
        
        #print "tbin %-11.7f tbinp %-11.7f tbinn %-11.7f" % (self.tbin, self.tbinp, self.tbinn)
        fp = open(self.fname, "w")
        fp.write ("[\n")
        fp.close()
        
    def work(self, input_items, output_items):
        """Do dedispersion/folding"""
        q = input_items[0]
        l = len(q)
        if (l > self.max_in):
            self.max_in = l
        elif (l < self.min_in):
            self.min_in = l
        for i in range(l/self.flen):
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
            #   total time-bins (self.tbint) modulo the profile length
            #
            # Update all the profiles
            #
            for i in range(len(self.profiles)):
                where = self.MET/self.tbint[i]
                where = int(where) % self.plen
                self.profiles[i][where] += outval
                self.pcounts[i][where] += 1
            
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
                fp = open(self.fname, "a")
                outputs = []
                for i in range(len(self.profiles)):
                    outputs.append(np.divide(self.profiles[i],self.pcounts[i]))
                d = {}
                t = time.gmtime()
                d["time"] = "%04d%02d%02d-%02d:%02d:%02d" % (t.tm_year,
                    t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                d["sequence"] = self.sequence
                d["max_input_length"] = self.max_in
                d["min_input_length"] = self.min_in
                self.sequence += 1
                profiles = []
                for i in range(len(self.profiles)):
                    pd = {}
                    pd["profile"] = list(outputs[i])
                    pd["p0"] = self.p0*(1.0+self.shifts[i])
                    pd["shift"] = self.shifts[i]
                    profiles.append(pd)
                d["profiles"] = profiles
                fp.write(json.dumps(d, indent=4, sort_keys=True)+",\n")
                fp.close()
                self.logcount = self.INTERVAL
            
            
        return len(q)
