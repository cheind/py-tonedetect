

import argparse
import logging
import threading
import sys

from examples.pipeline import DefaultDetectionPipeline
from tonedetect import helpers
from tonedetect.tones import Tones
from tonedetect import sources
from datetime import datetime

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
    
    # Setup input source
    source = None
    if args.subparser_name == 'ffmpeg':
        source = sources.FFMPEGSource(args.source, args.ffmpeg, args.sample_rate)    

    pipeline = DefaultDetectionPipeline(
        source, tones, 
        min_tone_amp=args.min_tone_level,
        max_inter_tone_amp=args.max_tone_range,
        min_presence=args.min_tone_on,
        min_pause=args.min_tone_off,
        max_tone_interval=args.max_tone_interval,
        min_sequence_length=args.min_seq_length
    )
    
    periodic_status()
    for w in pipeline.read():
        seq, start, stop = pipeline.detect(w)
        if len(seq) > 0:
            logger.info(">>> {} around {:.2f}-{:.2f}".format("".join([str(e) for e in seq]), start, stop))
            status['sequences'].append(seq)

        status['update'] = datetime.now()
        status['bytes'] = source.bytes_processed
    

if __name__ == "__main__":
    main()
    