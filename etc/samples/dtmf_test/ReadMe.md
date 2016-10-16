
## Filename interpretation

This directory contains wav files to be used in conjunction with the `test_dtmf_pipeline.py` test. Each wav file represents a sequence to be detected. The expected sequence characters are encoded in the filename and are according to the following table

|Character|Meaning|
|---------|-------|
|0..9|Numbers 0..9|
|A,B,C,D|Characters A,B,C,D|
|s|Star `*`|
|p|Hash `#`|
|P|Long pause of 1sec, ignored in detection|
|d|Short pause of 100ms, ignored in detection|
|--|Everythin after -- is ignored in detection|

## Capture Methods

Pure DTMF tone sequences are generated through http://dialabc.com/sound/generate/

Radio overlayed signals are generated tuning into a talk radio station and outputting via ordinary speakers. Pure DTMF sequences are overlayed at random timepoints. The mixed output is captured by a microphone at 8000Hz sampling rate and saved as PCM16 WAV file.