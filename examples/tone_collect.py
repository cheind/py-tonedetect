

import argparse
import logging
import threading
import sys
import itertools
from datetime import datetime

from tonedetect import helpers
from tonedetect.tones import Tones
from tonedetect.sources import FFMPEGSource, STDINSource, SilenceSource
from tonedetect.window import Window
from tonedetect.detectors import FrequencyDetector, ToneDetector, ToneSequenceDetector

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S", level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():

    def add_common_args(parser):
        parser.add_argument("--tones", help="Json file containing the tone description.", required=True)
        parser.add_argument("--sample-rate", type=int, help="Sample rate of input audio in Hertz", default=44100)
        parser.add_argument("--min-tone-level", type=float, help="Minimum tone amplitude [0..1]", default=0.1)
        parser.add_argument("--max-tone-range", type=float, help="Maximum amplitude range between frequencies of a specific tone [0..1]", default=0.1)
        parser.add_argument("--min-tone-on", type=float, help="Minimum time for tones to be active before detected in seconds", default=0.04)
        parser.add_argument("--min-tone-off", type=float, help="Minimum time non-active time for a tone before detection stops in seconds", default=0.04)
        parser.add_argument("--max-tone-interval", type=float, help="Maximum time between two tones so that both tones belong to same sequence in seconds", default=1)
        parser.add_argument("--min-seq-length", type=int, help="Minimum length or tone sequences to be recognized", default=2)

    parser = argparse.ArgumentParser(prog="tone_collect")
    subparsers = parser.add_subparsers(help="sub-command help", dest="subparser_name")

    parser_ffmpeg = subparsers.add_parser("ffmpeg", help="Tone collecting from FFMPEG")
    add_common_args(parser_ffmpeg)
    parser_ffmpeg.add_argument("--ffmpeg", help="Path to FFMPEG executable.", default="ffmpeg")
    parser_ffmpeg.add_argument("--source", help="The audio input. Can be a local file path or remote stream address.", required=True)

    parser_stdin = subparsers.add_parser("stdin", help="Tone collecting from standard input")
    parser_stdin.add_argument("--source-type", help="How binary data from stdin is interpreted", default="int16")
    add_common_args(parser_stdin)  

    args = parser.parse_args()
    if args.subparser_name is None:
        print("No subcommand given.")
        parser.print_usage()
        sys.exit(1)
    return args
        
status = {
    'sequences': [],
    'since': datetime.now(),
    'update': datetime.now(),
    'bytes': 0
}

def periodic_status():
    logger.info(
        "Status {} sequences, running since: {}, last updated: {}, bytes processed: {}"
        .format(
            len(status['sequences']), 
            helpers.pretty_date(status['since'], suffix=""), 
            helpers.pretty_date(status['update']),
            helpers.pretty_size(status['bytes'])
        )
    )
    t = threading.Timer(10, periodic_status)
    t.daemon = True
    t.start()

def main():
    
    args = parse_args()

    # Load tones description    
    logger.info("Loading tone description from '{}'".format(args.tones))
    tones = Tones.from_json_file(args.tones)
    freqs = tones.all_tone_frequencies()
    
    # Setup input source
    data_source = None
    if args.subparser_name == "ffmpeg":
        logger.info("Initializing FFMPEG source")
        data_source = FFMPEGSource(args.source, ffmpeg_binary=args.ffmpeg, sample_rate=args.sample_rate)
    elif args.subparser_name == "stdin":
        logger.info("Initializing STDIN source")
        data_source = STDINSource(sample_rate=args.sample_rate, source_type=args.source_type)

    # Setup silence source
    silence_source = SilenceSource(args.max_tone_interval*2, args.sample_rate)

    # Setup overlapping data window
    wnd = Window.tuned(args.sample_rate, freqs, power_of_2=True)
    
    d_f = FrequencyDetector(freqs)
    
    d_t = ToneDetector(
        tones, 
        min_tone_amp=args.min_tone_level, 
        max_inter_tone_amp=args.max_tone_range, 
        min_presence=args.min_tone_on, 
        min_pause=args.min_tone_off
    )

    d_s = ToneSequenceDetector(
        max_tone_interval=args.max_tone_interval, 
        min_sequence_length=args.min_seq_length
    )

    data_gen = itertools.chain(data_source.generate_parts(), silence_source.generate_parts())
    
    periodic_status()
    for chunk in data_gen:
        for w in wnd.update(chunk):
            cur_freqs = d_f.update(w) 
            cur_tones = d_t.update(w, cur_freqs)
            seq, start, stop = d_s.update(w, cur_tones)

            if len(seq) > 0:
                logger.info(">>> {} around {:.2f}-{:.2f}".format("".join([str(e) for e in seq]), start, stop))
                status['sequences'].append(seq)
    
        status['update'] = datetime.now()
        status['bytes'] = data_source.bytes_processed
    

if __name__ == "__main__":
    main()
    