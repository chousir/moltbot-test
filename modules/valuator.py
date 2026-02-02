import requests
import datetime
from datetime import timedelta
import time
from modules.base_analyst import BaseAnalyst
from utils.data_manager import DataManager

class Valuator(BaseAnalyst):
    def __init__(self):
        super().__init__("The Valuator (Fundamental)")
        self.dm = DataManager()
        self.specialty = "Calculating intrinsic value, dividends, and earnings quality."
        self.persona = "A conservative, value-oriented accountant who hates overpaying for growth."
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Alpha/1.0"
        })

    def _get_taiwan_date(self, lookback_days=0):
        utc_now = datetime.datetime.utcnow()
        tw_now = utc_now + timedelta(hours=8)
        target_date = tw_now - timedelta(days=lookback_days)
        return target_date

    def _fetch_bwibbu_data(self, date_obj):
        """Fetch PE, PB, Yield with caching"""
        date_str = date_obj.strftime("%Y%m%d")
        
        # Try Cache
        cached = self.dm.load_data("TWSE_BWIBBU", date_str, max_age_hours=12)
        if cached:
            return cached

        url = f"https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?date={date_str}&selectType=ALL&response=json"
        
        try:
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data['stat'] != 'OK':
                return None
            
            # Save to Cache
            self.dm.save_data("TWSE_BWIBBU", date_str, data['data'])
            return data['data']
        except Exception:
            return None

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Assessing intrinsic value for {ticker}...")
        
        # 1. Input Validation (Security)
        # Prevent injection by ensuring ticker is strictly alphanumeric/dot
        if not ticker.replace('.', '').isalnum(): 
             return {"signal": "NEUTRAL", "confidence": 0, "reason": "Invalid Ticker Format", "data": {}}

        stock_id = ticker.split('.')[0]
        
        # 2. Fetch Data (Retry logic)
        found_data = None
        target_date = None
        
        for i in range(5):
            date_check = self._get_taiwan_date(i)
            if date_check.weekday() > 4: continue
            
            raw_data = self._fetch_bwibbu_data(date_check)
            if raw_data:
                found_data = raw_data
                target_date = date_check.strftime("%Y-%m-%d")
                break
            time.sleep(1)

        if not found_data:
            return {
                "signal": "NEUTRAL", 
                "confidence": 0, 
                "reason": "No Fundamental Data Found (TWSE)", 
                "data": {}
            }

        # 3. Locate Stock
        # TWSE format: stock_id is usually index 0
        stock_row = next((row for row in found_data if row[0] == stock_id), None)
        
        if not stock_row:
             return {
                "signal": "NEUTRAL", 
                "confidence": 0, 
                "reason": f"Stock {stock_id} not in valuation report", 
                "data": {}
            }

        try:
            # Parse Data (Handle '-' for negative earnings/losses)
            # Index 2: Yield (%), Index 4: PE, Index 5: PB
            def parse_float(val):
                if val == '-' or val == '': return None
                if isinstance(val, (int, float)): return float(val) # Already a number
                return float(str(val).replace(',', ''))

            dy_yield = parse_float(stock_row[2]) # Dividend Yield
            pe_ratio = parse_float(stock_row[4]) # PE
            pb_ratio = parse_float(stock_row[5]) # PB

            score = 0
            reasons = []

            # --- Valuation Logic ---

            # A. Dividend Yield Strategy (Cash Cow)
            if dy_yield:
                if dy_yield > 5.0:
                    score += 1.0
                    reasons.append(f"High Yield ({dy_yield}%)")
                elif dy_yield < 1.0:
                    score -= 0.5
            
            # B. PE Ratio Strategy (Growth vs Value)
            if pe_ratio:
                if pe_ratio < 12:
                    score += 1.0
                    reasons.append(f"Undervalued PE ({pe_ratio})")
                elif pe_ratio > 30:
                    score -= 0.5
                    reasons.append(f"Premium PE ({pe_ratio})")
            else:
                # If PE is '-' it usually means negative earnings
                score -= 2.0
                reasons.append("Negative Earnings (Loss)")

            # C. PB Ratio Strategy (Safety)
            if pb_ratio:
                if pb_ratio < 1.0:
                    score += 1.0
                    reasons.append(f"Below Book Value (PB {pb_ratio})")
                elif pb_ratio > 6.0:
                    score -= 0.5
            
            # Final Decision
            if score >= 1.5:
                signal = "BUY"
                confidence = 0.8
            elif score <= -1.0:
                signal = "SELL"
                confidence = 0.8
            else:
                signal = "NEUTRAL"
                confidence = 0.5
                reasons.append("Valuation Fair")

            return {
                "signal": signal,
                "confidence": confidence,
                "reason": "; ".join(reasons),
                "data": {
                    "Date": target_date,
                    "Yield": f"{dy_yield}%" if dy_yield else "N/A",
                    "PE": pe_ratio if pe_ratio else "Loss",
                    "PB": pb_ratio if pb_ratio else "N/A"
                }
            }

        except Exception as e:
             return {
                "signal": "NEUTRAL", 
                "confidence": 0, 
                "reason": f"Parse Error: {e}", 
                "data": {}
            }
