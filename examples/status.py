
import logging
import threading
from datetime import datetime
from tonedetect import helpers

class Status:
    def __init__(self):
        self.sequences = []
        self.since = datetime.now()
        self.last_update = datetime.now()
        self.bytes_processed = 0

    def update_bytes(self, total_bytes):
        self.bytes_processed = total_bytes
        self.last_update = datetime.now()

    def update_sequences(self, new_sequence):
        self.sequences.append(new_sequence)
        self.last_update = datetime.now()

class StatusPrinter:
    def __init__(self, status):
        self.status = status
        self.logger = logging.getLogger(__name__)

    def start_periodic_print(self, refresh_interval=5):
        self.logger.info(
            "Status {} sequences, running since: {}, last updated: {}, bytes processed: {}"
            .format(
                len(self.status.sequences), 
                helpers.pretty_date(self.status.since, suffix=""), 
                helpers.pretty_date(self.status.last_update),
                helpers.pretty_size(self.status.bytes_processed)
            )
        )
        t = threading.Timer(refresh_interval, self.start_periodic_print)
        t.daemon = True
        t.start()
