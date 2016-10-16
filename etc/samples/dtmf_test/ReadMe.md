This directory contains wav files to be used in conjunction with the `test_dtmf_pipeline.py` test. Each wav file represents a sequence to be detected. The expected sequence characters are encoded in the filename and are according to the following table

|Character|Meaning|
|---------|-------|
|0..9|Numbers 0..9|
|A,B,C,D|Characters A,B,C,D|
|s|Star `*`|
|p|Hash `#`|
|P|Long pause of 1sec, ignored in detection|
|d|Short pause of 100ms, ignored in detection|

Most of the tones found in this directory are generated using 