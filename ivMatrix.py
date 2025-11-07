

import os, requests, json

from datetime import date, timedelta, datetime


class IvMatrix:

# AI HELPERS #

    def __init__(self,ticker,api_key,side):
        self.api_key = api_key
        self.ticker = ticker
        self.side = side

    def get_fridays():
        today = date.today()
        end_date = today + timedelta(days=365)
        fridays = []
        # Find the next Friday (weekday() == 4)
        days_until_friday = (4 - today.weekday()) % 7
        next_friday = today + timedelta(days=days_until_friday)

        while next_friday <= end_date:
            fridays.append(next_friday.strftime("%Y-%m-%d"))
            next_friday += timedelta(days=7)

        return fridays

    def days_until(target_date_str):
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        today = date.today()
        return (target_date - today).days

#My code: workking with api

    def fulfill_request(self,request):
        output = []
        r = requests.get(request)
        r.raise_for_status()
        pull = r.json()
        output.extend(pull["results"])
        
        nextUrl = pull.get("next_url")
        if nextUrl == None:
            return output
        
        while nextUrl != None:
            r = requests.get(nextUrl, params={"apiKey": self.api_key})
            r.raise_for_status()
            pull = r.json()
            output.extend(pull.get("results"))
            nextUrl = pull.get("next_url")
            
        return output

    def get_data(self,exp,limit=250):
        request = f"https://api.massive.com/v3/snapshot/options/{self.ticker}?expiration_date={exp}&contract_type={self.side}&order=asc&limit=250&sort=expiration_date&apiKey={self.api_key}"
        return self.fulfill_request(request)

    def get_IV_chain(self,exp):
        matrix = {}
        data = self.get_data(exp)
        for d in data:
            details = d.get("details")
            strike = details.get("strike_price")
            IV = d.get("implied_volatility")
            if IV != None:
                matrix[strike] = IV
        return matrix

    def get_IV_matrix(self):
        matrix = {}
        expiries = IvMatrix.get_fridays()
        for exp in expiries:
            chain = self.get_IV_chain(exp)
            if chain != {}:
                matrix[IvMatrix.days_until(exp)] = chain

        return matrix

