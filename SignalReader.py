from dataclasses import dataclass

import asyncio
import serial
from typing import Callable, List

import time

@dataclass
class BeaconSignal:
    ssid: str
    mac: str
    rssi: float
    timestamp: float

    @staticmethod
    def from_str(data: str):
        if data[0] == '|':
            ssid = ""
            mac, rssi = data.split("|")
        else:
            ssid, mac, rssi = data.split("|")

        return BeaconSignal(ssid, mac, float(rssi), time.time())
    
@dataclass
class SignalReader:
    on_signal: Callable[[BeaconSignal], None]
    dev: str = "/dev/ttyUSB0"
    comment_prefix: str = "//", 
    on_comment: Callable[[str], None] | None = print
    
    async def run(self):
        try:
            with serial.Serial(self.dev, baudrate=115200) as ser:
                print(f"openning {self.dev}")
                ser.readline()
                while True:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode().strip()

                        # ignore "comment" lines
                        if line.startswith(self.comment_prefix):
                            if self.on_comment:
                                self.on_comment(line)
                        else:
                            s = BeaconSignal.from_str(str(line))
                            self.on_signal(s)
                    
                    await asyncio.sleep(0)
        except serial.SerialException:
            print(f"failed to open device {self.dev}")
            
                    
            


if __name__ == "__main__":
    reader = SignalReader()
    while True:
        signals = reader.read_signals()

        if len(signals) > 0:
            print(signals)

        time.sleep(0.1)