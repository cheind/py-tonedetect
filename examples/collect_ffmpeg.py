

import argparse
import logging
import threading

from examples.pipeline import DefaultDetectionPipeline
from tonedetect import helpers
from tonedetect.tones import Tones
from tonedetect import sources
from datetime import datetime

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="the source of audio. Can be a local file path or remote stream address.")
    parser.add_argument("--tones", help="the json file containing the tone description.", required=True)
    parser.add_argument("--samplerate", type=int, help="Desired sample rate of audio", default=44100)
    parser.add_argument("--ffmpeg", help="Path to FFMPEG executable.", default="ffmpeg")
    parser.add_argument("--buffersize", help="buffer size for process pipes", type=int, default=1024)

    return parser.parse_args()



status = {
    'sequences': [],
    'since': datetime.now(),
    'update': datetime.now()
}

def print_status():
    logger.info("Status: found {} sequences, running since: {}, last updated: {}".format(len(status['sequences']), helpers.pretty_date(status['since'], suffix=""), helpers.pretty_date(status['update'])))
    t = threading.Timer(10, print_status)
    t.daemon = True
    t.start()

def main():
    
    args = parse_args()
    tones = Tones.from_json_file(args.tones)
    
    gen_parts = sources.FFMPEGSource.generate_parts(
        args.source,
        ffmpeg_binary=args.ffmpeg,
        sample_rate=args.samplerate,
        part_length=args.buffersize)

    pipeline = DefaultDetectionPipeline(gen_parts, args.samplerate, tones)
    
    print_status()
    for w in pipeline.read():
        seq, start, stop = pipeline.detect(w)

        if len(seq) > 0:
            logger.info("Sequence found! {} around {:.2f}-{:.2f}".format(seq, start, stop))
            status['sequences'].append(seq)

        status['update'] = datetime.now()
    

if __name__ == "__main__":
    main()
    