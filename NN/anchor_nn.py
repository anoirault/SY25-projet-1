import math
import torch


class Anchor_NN:
    def __init__(self, x, y, M, N):
        self.x = x
        self.y = y
        
        self.M = M
        self.N = min(4, max(N, 2))
        
    def distance(self, x:float, y:float):
        return abs(((self.x-x)**2 + (self.y-y)**2)**(1/2))
    
    def rssi(self, x:float, y:float):
        d = self.distance(x, y)
        d = d if d != 0 else d +.01
        return -10*self.N*math.log10(d) + self.M
    
    def sample(self, x:float, y:float, nSample=100, std=5):
        rssi = torch.ones(nSample)*self.rssi(x, y)
        noise = torch.randn(nSample)*std
        return rssi + noise
        