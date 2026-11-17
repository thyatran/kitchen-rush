"""Round-local plate inventory. Plates in transit are represented by objects."""
from dataclasses import dataclass


@dataclass
class Plate:
    state: str = 'dirty'

    @property
    def label(self):
        return f'{self.state} plate'


class PlateSupply:
    def __init__(self, count=3):
        self.clean = count
        self.dirty = 0
        self.pending_returns = []

    def take_clean(self):
        if not self.clean:
            return False
        self.clean -= 1
        return True

    def return_dirty(self):
        self.dirty += 1

    def schedule_return(self):
        self.pending_returns.append(3.0)

    def update(self, dt):
        remaining = []
        for timer in self.pending_returns:
            timer -= dt
            if timer <= 1e-9:
                self.dirty += 1
            else:
                remaining.append(timer)
        self.pending_returns = remaining

    def collect_dirty(self):
        if not self.dirty:
            return None
        self.dirty -= 1
        return Plate()

    def store_clean(self):
        self.clean += 1
