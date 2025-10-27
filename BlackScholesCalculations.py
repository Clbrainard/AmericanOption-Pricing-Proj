import math
import numpy as np
from scipy.integrate import quad
import sys

class BScalculator:

    def call(S,K,v,r,q,T):
        A = S * math.exp(-q * T) * BScalculator.N(BScalculator.D1(S,K,v,r,q,T))
        B = K * math.exp(-r * T) * BScalculator.N(BScalculator.D2(S,K,v,r,q,T))
        return A-B
    
    def put(S,K,v,r,q,T):
        A = K * math.exp(-r * T) * BScalculator.N(-BScalculator.D2(S,K,v,r,q,T))
        B = S * math.exp(-q * T) * BScalculator.N(-BScalculator.D1(S,K,v,r,q,T))
        return A-B

    def D1(S,K,v,r,q,T):
        A = math.log(S / K)
        B = (r-q+((v**2)/2)) * T
        C = v * math.sqrt(T)
        return (A+B)/C

    def D2(S,K,v,r,q,T):
        C = v * math.sqrt(T)
        return BScalculator.D1(S,K,v,r,q,T) - C

    def N(x: float) -> float:
        # Standard normal CDF
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def n(x):
        A = math.sqrt(2*math.pi)
        B = math.exp(-(x**2)/2)
        return B/A

    def Vega(S,K,v,r,q,T):
        A = S * math.exp(-q * T)
        B = BScalculator.n(BScalculator.D1(S,K,v,r,q,T)) * math.sqrt(T)
        return max(A*B,sys.float_info.min)
    
    def get_vol_from_price(S, K, r, q, T, Cm, E=1e-6, V0=0.2, max_iter=100):
        v = V0
        for _ in range(max_iter):
            price = BScalculator.call(S, K, v, r, q, T)
            diff = price - Cm
            if abs(diff) < E:
                return v
            vega = BScalculator.Vega(S, K, v, r, q, T)
            if vega < 1e-8:  # avoid division by zero
                break
            v -= diff / vega
            if v <= 0:
                v = 1e-8  # volatility cannot be negative
        return float('nan')  # didn't converge
    