import yfinance as yf
from datetime import datetime, timedelta
import math
import pandas_datareader.data as web

class riskFreeAsset:
    def __init__(self, rate):
        self.rate = rate  # annual risk-free rate

    def get_expected_return(self):
        return self.rate / 252  # daily return if needed

    def get_variance(self):
        return 0

    def get_standard_deviation(self):
        return 0

    def get_annualized_volatility(self):
        return 0
    
    def get_daily_returns(self):
        daily = []
        for x in range(252):
            daily.append(self.rate / 252)

        return daily


class stock:

    def __init__(self,ticker):
        self.ticker = ticker
        self.closes = self.get_historical_closes()
        
    def get_historical_closes(self):
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        data = web.DataReader(self.ticker, "stooq", start_date, end_date)
        data = data.sort_index()

        daily_closes = data['Close']
        closes_list = daily_closes.tolist()
        
        return closes_list
    
    #past year
    def get_daily_returns(self):
        closes = self.closes
        daily_returns = []
        for i in range(1,len(closes)):
            daily_returns.append((closes[i]-closes[i-1]) / closes[i-1])

        return daily_returns

    def get_expected_return(self): 
        returns = self.get_daily_returns()
        return sum(returns) / (len(returns) - 1)
        
    def get_variance(self):
        returns = self.get_daily_returns()
        expected = self.get_expected_return()
        summation = 0

        for R in returns:
            summation += (R - expected) ** 2

        return summation/ (len(returns) - 1)
    
    def get_covariance(stockA,stockB):
        returnsA = stockA.get_daily_returns()
        expectedA = stockA.get_expected_return()
        returnsB = stockB.get_daily_returns()
        expectedB = stockB.get_expected_return()
        summation = 0

        for RA, RB in zip(returnsA,returnsB):
            summation += (RA-expectedA) * (RB-expectedB)

        return summation / (len(returnsA)-1)

    def get_standard_deviation(self):
        return math.sqrt(self.get_variance())

    def get_annualized_volatility(self):
        std = self.get_standard_deviation()
        return std * math.sqrt(252)

    def get_correlation(stockA, stockB):
        stdA = stockA.get_standard_deviation()
        stdB = stockB.get_standard_deviation()
        cov = stock.get_covariance(stockA,stockB)

        return cov / (stdA * stdB)

# Example usage:
if __name__ == "__main__":
    #A = stock("AAPL")
    #B = stock("NVDA")
    C = riskFreeAsset(0.05)
    print(C.get_expected_return())
