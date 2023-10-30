import os

import torch
import torch.nn as nn

class Regressor(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.encode = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=2, kernel_size=(3, 5)),
            nn.ReLU(),
            nn.Conv2d(in_channels=2, out_channels=4, kernel_size=(1, 5)),
            nn.ReLU()
        )
        self.mu = nn.Sequential(            # nn.Flatten(),
            nn.Linear(in_features=2*92*4, out_features=4*2*9),
            nn.ReLU()
        )
        self.sigma = nn.Sequential(
            nn.Linear(in_features=2*92*4, out_features=4*2*9),
            nn.ReLU()
        )
        self.decodeLin = nn.Sequential(
            nn.Linear(in_features=4*2*9, out_features=2*92*4),
            nn.ReLU()
        )
        self.decode = nn.Sequential(
            nn.ConvTranspose2d(in_channels=4, out_channels=2, kernel_size=(1,5)),
            nn.ReLU(),
            nn.ConvTranspose2d(in_channels=2, out_channels=1, kernel_size=(3,5)),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(in_features=4*100, out_features=2)
        )
        
        
    def reparametrize(self, mu:torch.Tensor, log_sigma:torch.Tensor) -> torch.Tensor :
        std = torch.exp(log_sigma/2)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def forward(self, x):
        x = self.encode(x)
        
        x_shape = x.shape
        
        mu = self.mu(x.view(1,4*2*92))
        sigma = self.sigma(x.view(1,4*2*92))
        
        z = self.reparametrize(mu, sigma)
        
        z = self.decodeLin(z).view(x_shape)
        
        y = self.decode(z)
        
        return y
    
    def load(self, path, opti):
        ckpt = torch.load(path)
        self.load_state_dict(ckpt['model'])
        opti.load_state_dict(ckpt['opti'])
        return opti
    
    def save(self, opti):
        torch.save({
            'model':self.state_dict(),
            'opti':opti.state_dict()
        }, 'ckpt.pth')
        
    def create(self, lr=1e-3, load=True):
        
        reg = Regressor()
        
        opti = torch.optim.Adam(reg.parameters(), lr = lr)
        
        if os.path.exists('ckpt.pth') and load:
            opti = reg.load('ckpt.pth', opti)
            
        return reg, opti, nn.MSELoss()
        
    