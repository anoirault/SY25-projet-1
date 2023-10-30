# estim_y = [10 ** ((m - r)/(10 * n)) for r in estim_x]

from Anchor import Anchor


import time
from dataclasses import dataclass, field


@dataclass
class RssiSignal:
    origin: Anchor
    strength: float = -100
    time: float = field(default_factory=time.time)

    def older_than(self, age: float) -> bool:
        return self.time + age < time.time()
    
    def get_age(self, current_time: float | None = None) -> float:
        # use provided time if available else default to directly obtaining current time
        current_time = current_time or time.time()

        return current_time - self.time

    def esim_dist_to_anchor(self):
        return self.origin.esim_dist(self.strength)