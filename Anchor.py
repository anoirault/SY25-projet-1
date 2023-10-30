from dataclasses import dataclass
from typing import Tuple


@dataclass
class Anchor:
    position: Tuple[float, float]
    ssid: str = ""
    name: str = "Anchor"
    mac: str = "00:00:00:00:00:00"
    color: Tuple[int, int, int] = (255, 0, 0)

    m: float = -40.0
    n: float = 2.2
    
    num: int = 0

    def esim_dist(self, rssi: float) -> float:
        return 10 ** ((float(self.m) - rssi)/(10.0 * float(self.n)))
    
    def __hash__(self): return hash(id(self))

    def move(self, offset: Tuple[float, float]):
        self.position = (self.position[0] + offset[0], self.position[1] + offset[1])