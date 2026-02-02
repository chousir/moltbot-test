from modules.base_analyst import BaseAnalyst
from utils.data_manager import DataManager
import requests
import datetime
import pandas as pd
import time
from datetime import timedelta

class ChipWatcher(BaseAnalyst):
    def __init__(self):
        super().__init__("The Chip Watcher (Institutional)")
        self.dm = DataManager()
        self.session = requests.Session()
        self.specialty = "Tracking flow of 3 Major Institutional Investors (Foreign, Trust, Dealers)."
        self.persona = "A cynical detective who only believes in where the cold, hard cash is moving."
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Alpha/1.0"
        })

    def _get_taiwan_date(self, lookback_days=0):
        """Get date in Taiwan Timezone (UTC+8)"""
        utc_now = datetime.datetime.utcnow()
        tw_now = utc_now + timedelta(hours=8)
        target_date = tw_now - timedelta(days=lookback_days)
        return target_date

    def _fetch_twse_data(self, date_obj):
        """Fetch T86 data with local caching"""
        date_str = date_obj.strftime("%Y%m%d")
        
        # Try Cache First
        cached = self.dm.load_data("TWSE_T86", date_str, max_age_hours=12)
        if cached:
            return cached['data'], cached['fields']

        url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALL&response=json"
        
        try:
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data['stat'] != 'OK':
                return None, None
            
            # Save to Cache
            self.dm.save_data("TWSE_T86", date_str, {"data": data['data'], "fields": data['fields']})
            return data['data'], data['fields']
        except Exception:
            return None, None

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Connecting to TWSE (Taiwan Stock Exchange)...")
        
        # Handle Ticker Format (2330.TW -> 2330)
        stock_id = ticker.split('.')[0]
        if not stock_id.isdigit():
             return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": "Not a TWSE stock (Ticker format mismatch)",
                "data": {}
            }

        # Try to find the latest valid trading day (max 5 days lookback)
        found_data = None
        target_date = None
        fields_map = {}

        for i in range(5):
            date_check = self._get_taiwan_date(i)
            # Skip weekend roughly (simple check)
            if date_check.weekday() > 4: 
                continue
                
            raw_data, fields = self._fetch_twse_data(date_check)
            if raw_data:
                found_data = raw_data
                target_date = date_check.strftime("%Y-%m-%d")
                
                # Map fields
                # Typical Fields: ["證券代號","證券名稱","外資買進股數","外資賣出股數","外資買賣超股數", ... "投信買賣超股數", ... "自營商買賣超股數"]
                # We simply search for keywords
                try:
                    fields_map['foreign'] = [i for i, f in enumerate(fields) if '外資' in f and '買賣超' in f][0]
                    fields_map['trust'] = [i for i, f in enumerate(fields) if '投信' in f and '買賣超' in f][0]
                    fields_map['dealer'] = [i for i, f in enumerate(fields) if '自營商' in f and '買賣超' in f and '避險' not in f][0] # Simple Dealer
                except:
                    # Fallback or strict index (riskier if format changes)
                    pass
                break
            
            time.sleep(1) # Be polite

        if not found_data:
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": "No TWSE data found in last 5 days (Holiday?)",
                "data": {}
            }

        # Search for Ticker
        stock_row = next((row for row in found_data if row[0] == stock_id), None)
        
        if not stock_row:
             return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": f"Stock {stock_id} not found in T86 report",
                "data": {}
            }

        try:
            # Parse Values (They come as strings with commas like "12,345")
            def parse_val(s):
                return int(s.replace(',', ''))

            f_net = parse_val(stock_row[fields_map['foreign']]) # Foreign
            t_net = parse_val(stock_row[fields_map['trust']])   # Investment Trust
            d_net = parse_val(stock_row[fields_map['dealer']])  # Dealer

            # Logic
            score = 0
            reasons = []

            # 1. Foreign Investors (The big whale)
            if f_net > 1000000: # Buy > 1000 sheets
                score += 1.5
                reasons.append(f"Foreign Big Buy ({f_net//1000}张)")
            elif f_net < -1000000:
                score -= 1.5
                reasons.append(f"Foreign Big Sell ({f_net//1000}张)")
            elif f_net > 0:
                score += 0.5
            elif f_net < 0:
                score -= 0.5

            # 2. Investment Trust (The trend follower)
            if t_net > 0:
                score += 1.0 # Trust buying is a good signal in TW
                reasons.append(f"Trust Buy (+{t_net//1000}张)")
            elif t_net < 0:
                score -= 1.0
                reasons.append("Trust Sell")

            # Final Signal
            if score >= 2.0:
                signal = "BUY"
                confidence = 0.9
            elif score >= 1.0:
                signal = "BUY"
                confidence = 0.7
            elif score <= -2.0:
                signal = "SELL"
                confidence = 0.9
            elif score <= -1.0:
                signal = "SELL"
                confidence = 0.7
            else:
                signal = "NEUTRAL"
                confidence = 0.5

            return {
                "signal": signal,
                "confidence": confidence,
                "reason": "; ".join(reasons) if reasons else "Flow Neutral",
                "data": {
                    "Date": target_date,
                    "Foreign_Net": f"{f_net//1000}K",
                    "Trust_Net": f"{t_net//1000}K",
                    "Dealer_Net": f"{d_net//1000}K"
                }
            }

        except Exception as e:
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": f"Parsing Error: {str(e)}",
                "data": {}
            }
