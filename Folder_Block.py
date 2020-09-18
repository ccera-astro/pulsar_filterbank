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
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, fbsize=16,smear=10.0,period=0.714,filename='/dev/null',fbrate=2500):  # only default arguments here
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
        self.profile = np.array([0.0]*250)
        self.pcounts = np.array([0]*len(self.profile))
        
        #
        # Sample period
        #
        self.sper = 1.0/fbrate
        
        #
        # Mission Elapsed Time
        #
        self.MET = 0.0
        
        self.tbin = self.p0/len(self.profile)
        
        #
        # Open the output file
        #
        self.fp = open(filename, "w")
        
        self.INTERVAL = fbrate*30
        self.logcount = self.INTERVAL
            
    def work(self, input_items, output_items):
        """example: multiply with constant"""
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
                outval = sum(q[(i*self.flen):(i*self.flen)+self.flen])
            
            #
            # Figure out where this sample goes in the profile buffer, based on MET
            #
            where = self.MET/self.tbin
            where = int(where)
            if (where >= len(self.profile)):
                where = 0
                
            self.profile[where] += outval
            self.pcounts[where] += 1
            
            self.MET += self.sper
            self.logcount -= 1
            if (self.logcount <= 0):
                output = np.divide(self.profile,self.pcounts)
                self.fp.write(str(output)+"\n")
                self.fp.flush()
                self.logcount = self.INTERVAL
            
            
        return len(q)
