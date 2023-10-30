from Anchor import Anchor
from RssiSignal import RssiSignal


import asyncio
from dataclasses import dataclass
from random import choice, random
from typing import Callable, List


@dataclass
class SignalGenerator:
    on_signal: Callable[[RssiSignal], None]
    anchors: List[Anchor]

    async def run(self):
        while True:
            a = choice(self.anchors)
            
            strength = random() * 10 - 60

            r = RssiSignal(a, strength)

            self.on_signal(r)
            await asyncio.sleep(max(0, random() - 0.9))