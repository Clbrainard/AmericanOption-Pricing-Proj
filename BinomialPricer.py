
from ivSurface import IvSurface as IVS
import math



class OptionBinomial:

    def __init__(self,api_key,r,ticker,initial_price,strike,time_to_maturity,div_yield,side="call",steps=10):
        self.api_key = api_key
        self.r = r
        self.ticker = ticker
        self.So = initial_price
        self.T = time_to_maturity
        self.K = strike
        self.N = steps
        self.Q = div_yield
        self.Vol =  IVS(ticker,api_key,side).surface
        self.side = side
        self.dT = self.T / self.N
        self.R = math.exp((self.r - self.Q)*self.dT)
        self.discount_factor = math.exp(-self.r * self.dT)
        self.P_Tree = self.get_price_binomial_tree()
        self.V_Tree = self.get_V_tree()
        

    def get_price_binomial_tree(self):
        tree = [([self.So], None)]
        for i in range(1,self.N+1):
            t = i*self.dT
            params = self.get_params(t)

            prev_prices = tree[i-1][0]
            new_prices = []
            for price in prev_prices:
                new_prices.append(price*params["u"]) #up
                new_prices.append(price*params["d"]) #down
            tree.append((new_prices,params))
        return tree
    
    def get_params(self,t):
        v = self.Vol(t*365,self.K) 
        u = math.exp(v * math.sqrt(self.dT))
        d = 1.0 / u

        if abs(u - d) < 1e-12:
            u *= 1.0 + 1e-12
            d = 1.0 / u

        p = (self.R - d) / (u - d)

        if not (0.0 <= p <= 1.0):
            p = min(1.0, max(0.0, p))

        q = 1.0 - p
        return {"v": v, "u": u, "d": d, "p": p, "q": q}


    def get_terminal_set(self):
        terminal_P = self.P_Tree[self.N][0]
        terminal_V = []
        for price in terminal_P:
            terminal_V.append(self.get_intrinsic(price))
        return terminal_V
    
    def get_intrinsic(self,S):
        if self.side == "call":
            return max(0,S - self.K)
        else:
            return max(self.K - S,0)
    
    def get_V_tree(self):
        v_tree = [self.get_terminal_set()]
        p_tree = self.P_Tree

        for i in reversed(range(len(p_tree)-1)):
            params = p_tree[i+1][1]
            layer = []
            prices_i = p_tree[i][0]
            for k in range(len(prices_i)):
                A = params["p"] * v_tree[0][2*k]
                B = params["q"] * v_tree[0][(2*k)+1]
                EV = (A + B) * self.discount_factor
                IV = self.get_intrinsic(prices_i[k])
                layer.append(max(EV, IV, 0))
            v_tree.insert(0, layer)
        return v_tree
                
    def get_V0(self):
        return self.V_Tree[0][0]
    
    def get_delta(self):
        
        Su = self.P_Tree[1][0][0]
        Sd = self.P_Tree[1][0][1]
        S0 = self.P_Tree[0][0][0]
        dS = Su - Sd
        A = self.V_Tree[1][0] - self.V_Tree[1][1]
        return A / dS

