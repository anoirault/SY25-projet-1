from NN.anchor_nn import Anchor_NN
from NN.regressor import Regressor

import torch

class Wrapper:
    def __init__(self):
        
        learning_rate = 1e-3
        self.reg, self.opti, self.lossF = Regressor().create(lr=learning_rate, load=True)

        a1 = Anchor_NN(  0,   0, -42, 2.5)
        a2 = Anchor_NN(4.5,   0, -33, 2.2)
        a3 = Anchor_NN(  0, 6.5, -41, 2.2)
        a4 = Anchor_NN(4.5, 6.5, -50, 2. )

        self.a = [a1, a2, a3, a4]
        
        self.feature = [[0]*100]*4
        self.nSample = [0]*4
        
        
    def changeCoord(self, x, y, a):
        self.a[a].x = x
        self.a[a].y = y
        
    def changeParam(self, M, N, a):
        self.a[a-1].M = M
        self.a[a-1].N = min(4, max(N, 2))
        
        
    def train(self, x, y, feature, save=True):
        
        label = torch.tensor([x, y]).unsqueeze(0)
        
        sample = torch.tensor(feature).unsqueeze(0).unsqueeze(0)        
        
        out_label = self.reg(sample)
        loss = self.lossF(label, out_label)
        
        self.opti.zero_grad()
        loss.backward()
        self.opti.step()
        
        if save:
            self.reg.save(self.opti)
            
        
        return loss.data
        
    def addSample(self, numAncre, rssi):
        
        self.feature[numAncre-1][self.nSample[numAncre-1]] = rssi
                
        self.nSample[numAncre-1] = (self.nSample[numAncre-1]+1)%100
        
        
    def getCoord(self, feature, n=10):
        
        sample = torch.tensor(feature).unsqueeze(0).unsqueeze(0)  
        
        x, y = 0, 0
        
        for _ in range(n):
            x_out, y_out = self.reg(sample)[0] 
            
            x += x_out.data
            y += y_out.data
            
        x /= n
        y /= n
        
        return x, y
    
    def fakeTrain(self, niter, var=5, save=False):
        
        for i in range(niter):
            x = torch.randint(0, 41, (1,))/10
            y = torch.randint(0, 66, (1,))/10
            
            
            sample = torch.cat([anchor.sample(x.data, y.data, 100, var).unsqueeze(0) for anchor in self.a], 0).unsqueeze(0).unsqueeze(0)
            
            label = torch.tensor([x, y]).unsqueeze(0)
            
            
            out_label = self.reg(sample)
            loss = self.lossF(label, out_label)
            
            self.opti.zero_grad()
            loss.backward()
            self.opti.step()
            
    def fakeEvale(self, niter=30000, var=5):
        
        loss = 0
        for i in range(niter):
            x = torch.randint(0, 41, (1,))/10
            y = torch.randint(0, 66, (1,))/10
            
            
            sample = torch.cat([anchor.sample(x.data, y.data, 100, var).unsqueeze(0) for anchor in self.a], 0).unsqueeze(0).unsqueeze(0)
            
            label = torch.tensor([x, y]).unsqueeze(0)
            
            
            out_label = self.reg(sample)
            loss += self.lossF(label, out_label).data
            
        print(f"Loss for {niter} fake samples : {loss/niter}")
            