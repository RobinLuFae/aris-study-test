"""Explicit wall-clock limits, without scheduler or environment changes."""
import datetime
import json
import time
from pathlib import Path


class TrainingWindow:
    def __init__(self, budget_file, max_seconds):
        self.config = json.loads(Path(budget_file).read_text(encoding='utf-8'))
        self.deadline = datetime.datetime.fromisoformat(self.config['hard_deadline_utc'])
        self.reserve = self.config['checkpoint_reserve_seconds']
        self.started = time.monotonic()
        self.max_seconds = min(max_seconds, self.config['segment_seconds'])
        if self.max_seconds <= self.reserve:
            raise ValueError('Segment duration must exceed checkpoint reserve')
        if self.remaining_wall() <= self.reserve:
            raise RuntimeError('Approved training window has expired or lacks checkpoint reserve')

    def remaining_wall(self):
        return (self.deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds()

    def should_checkpoint(self):
        return (self.remaining_wall() <= self.reserve or
                time.monotonic()-self.started >= self.max_seconds-self.reserve)
