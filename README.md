# pulsar_filterbank
A Gnu Radio flow-graph for producing raw filterbank files from a live SDR

It produces 16-bit binary outputs, arranged from lowest to highest frequency
  in the filterbank output.

The code automatically determines suitable filterbank sizes and output
  rates.  A header file is produced that gives the calculated
  rates, etc.  The output file is in .FIL format, so it includes
  header information that makes it useful for downstream tools
  like the PRESTO toolsuite.

Also, a shell script, "pobserve" can be used to manage an observtion
with this Gnu Radio app.

Currently supported options:
<pre>

Usage: pulsar_filterbank.py: [options]

Options:
  -h, --help         show this help message and exit
  --bbgain=BBGAIN    Set Baseband Gain [default=10.0]
  --dec=DEC          Set Source DEC [default=54.5]
  --device=DEVICE    Set Hardware device string [default=airspy=0]
  --freq=FREQ        Set Tuner Frequency [default=612.0M]
  --fscale=FSCALE    Set Float to byte scaling [default=128]
  --ifgain=IFGAIN    Set IF Gain [default=10.0]
  --prefix=PREFIX    Set File prefix [default=./]
  --ra=RA            Set Source RA [default=3.51]
  --rfgain=RFGAIN    Set RF Gain [default=15.0]
  --runtime=RUNTIME  Set Total runtime (seconds) [default=600]
  --source=SOURCE    Set Source Name [default=B0329+54]
  --srate=SRATE      Set Hardware Sample Rate [default=2.5M]
  --startt=STARTT    Set Start Time [default=now]
</pre>
