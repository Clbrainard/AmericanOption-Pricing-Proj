

from surfaceAnalyzer import VolSurface
import math

class OptionTrinomial:

    def __init__(self,nj,ticker,S0,K,r,Q,T,side):
        self.S0 = S0
        self.ticker = ticker
        self.K = K
        self.r = r
        self.Q = Q
        self.T = T
        self.side =  side

        self.dS = (2*K) / nj
        self.Vol = VolSurface(ticker,self.S0,self.K,self.r,self.Q,side)
        self.dT = (self.dS ** 2) / (4 * self.Vol.get_vol(T) * (self.K ** 2))
        self.N = int(T / self.dT) + 1
        print(self.N,self.dT,self.dS)

        self.P_Trinomial = self.get_price_trinomial()

    def get_price_trinomial(self):
        tree = [[self.S0]]
        for j in range(1,self.N):
            tree.append([])
            for x in range(-j,j+1):
                tree[j].append(self.S0 + (x * self.dS))
        return tree
    
O = OptionTrinomial(50,"AAPL",262.8,250,0.04,0.004,12/365,"call")
