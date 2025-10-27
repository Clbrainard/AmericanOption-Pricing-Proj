from Data import Polygon as P
from BlackScholesCalculations import BScalculator as BS
from Securities import stock
import matplotlib.pyplot as plt

class TwoDimensionalVolSurface:

    def __init__(self,ticker,S0,K,r,q,side):
        self.ticker = ticker
        self.S0 = S0
        self.K = K
        self.r = r
        self.q = q
        self.side = side
        self.surface = self.get_vol_discrete_surface()
    
    def get_set_of_future_vols(self):
        data = P.get_cleaned_data(self.ticker,self.K,self.side)
        v0 = BS.get_vol_from_price(self.S0,self.K,self.r,self.q,data[0][0]/365,data[0][1])
        output = [(0,v0)]
        for t,p in data:
            vol = BS.get_vol_from_price(self.S0,self.K,self.r,self.q,t/365,p)
            output.append((t,vol))
        return output
    
    def get_vol_discrete_surface(self,N=10):
        data = self.get_set_of_future_vols()
        output = []

        for i in range(1,len(data[1:])):
            curr_t = data[i][0]
            curr_v = data[i][1]
            prev_t = data[i-1][0]
            prev_v = data[i-1][1]
            
            NT = (curr_t-prev_t) * N
            dT = (curr_t-prev_t) / (NT*365)
            dV = (curr_v-prev_v) / NT
            for k in range(0,NT):
                next = ((prev_t/365) + dT*k,prev_v + (k*dV))
                output.append(next)

        return output
    
    # T = days/365 ish
    def get_vol(self,T):
        highest = 0
        for t,v in self.surface:
            if T > t:
                highest = v
            else:
                break
        return highest
            
    def plot_surface(self):
        
        x, y = zip(*self.surface)

        # Create scatter plot
        plt.figure(figsize=(8, 5))
        plt.scatter(x, y, color='blue', s=50, label='Implied Volatility')
        plt.plot(x, y, color='gray', linestyle='--', alpha=0.7)  # optional: connect points

        # Label axes and title
        plt.title('Implied Volatility vs Time to Maturity')
        plt.xlabel('Time (days)')
        plt.ylabel('Implied Volatility')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.show()

#vol = VolSurface("AAPL",263,250,0.038,0.004,"call")
#vol.plot_surface()
