# pulsar_filterbank
A Gnu Radio flow-graph for producing raw filterbank files from a live SDR

It produces 16-bit binary outputs, arranged from lowest to highest frequency
  in the filterbank output.

The code automatically determines suitable filterbank sizes and output
  rates.  A header file is produced that gives the calculated
  rates, etc.


Currently supported options:


Usage: pulsar_filterbank.py: [options]

Options:

  -h, --help         show this help message and exit\
  --bbgain=BBGAIN    Set Baseband Gain [default=10.0]\
  --device=DEVICE    Set Hardware device string [default=airspy=0]\
  --freq=FREQ        Set Tuner Frequency [default=612.0M]\
  --fscale=FSCALE    Set Float to byte scaling [default=128]\
  --ifgain=IFGAIN    Set IF Gain [default=10.0]\
  --prefix=PREFIX    Set File prefix [default=./]\
  --rfgain=RFGAIN    Set RF Gain [default=15.0]\
  --runtime=RUNTIME  Set Total runtime (seconds) [default=600]\
  --srate=SRATE      Set Hardware Sample Rate [default=6.0M]
