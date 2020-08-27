# pulsar_filterbank
A Gnu Radio flow-graph for producing raw filterbank files from a live SDR

It produces 16-bit binary outputs, arranged from lowest to highest frequency
  in the filterbank output.

The code automatically determines suitable filterbank sizes and output
  rates.  A header file is produced that gives the calculated
  rates, etc.  The output file is in .FIL format, so it includes
  header information that makes it useful for downstream tools
  like the PRESTO toolsuite.

Also, a shell script, *observe_pulsar* can be used to manage an observtion
with this Gnu Radio app.

Currently supported options:
<pre>
Usage: pulsar_filterbank.py: [options]

Options:
  -h, --help            show this help message and exit
  --bbgain=BBGAIN       Set Baseband Gain [default=10.0]
  --dec=DEC             Set Source DEC [default=54.5]
  --device=DEVICE       Set Hardware device string [default=airspy=0]
  --dm=DM               Set Dispersion Measure [default=28.3]
  --dscale=DSCALE       Set Detector scaling [default=1]
  --freq=FREQ           Set Tuner Frequency [default=612.0M]
  --hp=HP               Set HP pass enable [default=1]
  --hpgain=HPGAIN       Set High Pass pseudo-gain [default=600.0m]
  --ifgain=IFGAIN       Set IF Gain [default=10.0]
  --pps=PPS             Set PPS source [default=internal]
  --prefix=PREFIX       Set File prefix [default=./]
  --pw50=PW50           Set Pulsar PW50 [default=6.6m]
  --ra=RA               Set Source RA [default=3.51]
  --refclock=REFCLOCK   Set Reference Clock Source [default=internal]
  --resolution=RESOLUTION
                        Set FB resolution multiplier [default=1]
  --rfgain=RFGAIN       Set RF Gain [default=15.0]
  --rfilist=RFILIST     Set RFI frequency list [default=]
  --rolloff=ROLLOFF     Set Enable Roll-off correction [default=1]
  --runtime=RUNTIME     Set Total runtime (seconds) [default=600]
  --source=SOURCE       Set Source Name [default=B0329+54]
  --srate=SRATE         Set Hardware Sample Rate [default=5.0M]
  --subdev=SUBDEV       Set Subdev spec, UHD-version only [default=A:0]
  --thresh=THRESH       Set RFI detection threshold--linear factor
                        [default=2.5]
  --wide=WIDE           Set Enable 16-bit output [default=0]
  --sky=SKY             Set independent SKY frequency.  [default=0]          
</pre>

The 'observe_pulsar' script makes some of this easier to deal with:

Usage: observe_pulsar <options>:

--name         Pulsar name. Default: B0329+54
--freq         Center frequency **IN MHz**.  Default: 408.0
--srate        Sample rate, **IN MHz**:  Default: 4.0
--rfgain       RF gain, usually in dB. Default: 40
--longitude    Local longitude. Negative is west.: Default: -76.03
--dscale       Detector scaling: Default: 1
--wide         Enable Wide (16 bit) samples Default: 0
--hp           Enable high-pass filter. Default: 0
--hpgain       Set "gain" on high-pass. Default: 0.6
--obstime      Observing time, **MINuTES**. Default: 5
               NOTE: A negative 'obstime' results in running immediately
               rather than waiting for the object to enter the FOV.
--prefix       Output file prefix. Default: ~
--rolloff      Enable roll-off correction
--sky          Set sky frequency


Appropriate pulsar parameters will be taken from a database of about 200 objects, included in this source package.
