
KEY = "HB7ZSa2dZbO5DjohKM7L3ll4JtpX1cZH"

import os
import requests
from datetime import datetime
from typing import List, Tuple, Optional, Literal, Union
from dotenv import load_dotenv
import os

class Polygon:
        
    Side = Optional[Literal["call", "put", "both"]]
    Result = Union[Tuple[str, float], Tuple[str, float, str]]

    def get_polygon_option_quotes(
        ticker: str,
        strike: float,
        side: Side = "both",
        api_key: Optional[str] = None,
        min_price: float = 0.0,
        timeout: float = 20.0,
        max_pages: int = 50
    ) -> List[Result]:
        """
        Robust snapshot fetch for all expirations at a given strike.

        - side: 'call' | 'put' | 'both' (default)
        - price fallback: mid(bid,ask) -> last_trade -> day.close -> break_even premium
        - safeguards: URL de-dupe, page cap, request timeouts
        """

        load_dotenv()
        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            raise ValueError("Set POLYGON_API_KEY or pass api_key=...")

        base = f"https://api.polygon.io/v3/snapshot/options/{ticker.upper()}"
        params = {
            "strike_price": strike,
            "sort": "expiration_date",
            "order": "asc",
            "limit": 250,
            "apiKey": api_key,
        }

        def _px(item: dict) -> Optional[float]:
            q = (item or {}).get("last_quote") or {}
            b, a = q.get("bid_price"), q.get("ask_price")
            if isinstance(b, (int, float)) and isinstance(a, (int, float)) and b > 0 and a > 0:
                return (b + a) / 2.0
            t = (item or {}).get("last_trade") or {}
            p = t.get("price")
            if isinstance(p, (int, float)) and p > 0:
                return float(p)
            day = (item or {}).get("day") or {}
            c = day.get("close")
            if isinstance(c, (int, float)) and c > 0:
                return float(c)
            be = item.get("break_even_price")
            typ = ((item.get("details") or {}).get("contract_type") or "").lower()
            if isinstance(be, (int, float)) and typ in {"call", "put"}:
                prem = (be - strike) if typ == "call" else (strike - be)
                if isinstance(prem, (int, float)) and prem > 0:
                    return float(prem)
            return None

        results: List[Result] = []
        next_url: Optional[str] = base
        first = True
        seen_urls = set()
        pages = 0

        with requests.Session() as s:
            while next_url:
                # stop if Polygon gives us a cursor we've already visited
                canonical = next_url if not next_url.startswith("/") else "https://api.polygon.io" + next_url
                if canonical in seen_urls:
                    break
                seen_urls.add(canonical)

                r = s.get(canonical, params=params if first else None, timeout=timeout)
                first = False
                r.raise_for_status()
                data = r.json() or {}
                pages += 1
                if pages > max_pages:
                    break

                for item in data.get("results", []) or []:
                    details = item.get("details") or {}
                    exp = details.get("expiration_date")  # 'YYYY-MM-DD'
                    typ = (details.get("contract_type") or "").lower()  # 'call'/'put'
                    if side in {"call", "put"} and typ != side:
                        continue
                    price = _px(item)
                    if price is None or price <= min_price:
                        continue
                    if side == "both":
                        results.append((exp, float(price), typ))
                    else:
                        results.append((exp, float(price)))

                # pagination
                next_url = data.get("next_url")
                if next_url:
                    if next_url.startswith("/"):
                        next_url = "https://api.polygon.io" + next_url
                    # IMPORTANT: never pass params after first page
                    params = None

        # sort by expiration (None to end)
        def _k(row):
            exp = row[0]
            try:
                return datetime.strptime(exp, "%Y-%m-%d")
            except Exception:
                return datetime.max

        results.sort(key=_k)
        return results
    
    #time in days
    #removes t=1
    def get_cleaned_data(ticker,strike,side):
        data = Polygon.get_polygon_option_quotes(ticker, strike, side)

        today = datetime.strptime("2025-10-24", "%Y-%m-%d")  # set 'today'
        result = [] 
        for date_str, value in data:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            delta_days = (date_obj - today).days
            days_until = 1 if delta_days == 0 else delta_days
            if days_until != 1:
                result.append((days_until, value))
            

        return result

