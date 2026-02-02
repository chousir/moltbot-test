from modules.base_analyst import BaseAnalyst
from utils.data_manager import DataManager
import requests
import pandas as pd
import datetime
from datetime import timedelta
import time

class WhaleHunter(BaseAnalyst):
    def __init__(self):
        super().__init__("The Whale Hunter (Large Holders)")
        self.dm = DataManager()
        self.api_url = "https://api.finmindtrade.com/api/v4/data"
        self.specialty = "Monitoring shareholding concentration and insider movements."
        self.persona = "A data scientist who looks for patterns in large-scale ownership shifts."

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Hunting for Whales in {ticker}...")
        
        stock_id = ticker.split('.')[0]
        
        # Determine date range
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Try Cache
        cached = self.dm.load_data("FINMIND_WHALE", stock_id, max_age_hours=168) # Weekly data
        if cached:
            data_list = cached
        else:
            start_date = (datetime.datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
            params = {
                "dataset": "TaiwanStockShareholding",
                "data_id": stock_id,
                "start_date": start_date,
                "end_date": end_date
            }
            try:
                resp = requests.get(self.api_url, params=params)
                data = resp.json()
                if data['msg'] != 'success' or not data['data']:
                    return {"signal": "NEUTRAL", "confidence": 0, "reason": "No Data", "data": {}}
                data_list = data['data']
                self.dm.save_data("FINMIND_WHALE", stock_id, data_list)
            except Exception:
                return {"signal": "NEUTRAL", "confidence": 0, "reason": "API Error", "data": {}}

        df = pd.DataFrame(data_list)
        df['date'] = pd.to_datetime(df['date'])
        latest_date = df['date'].max()
        prev_date = df[df['date'] < latest_date]['date'].max()
        
        if pd.isna(prev_date):
             return {"signal": "NEUTRAL", "confidence": 0, "reason": "Insufficient history", "data": {}}

        def get_whale_pct(d):
            subset = df[(df['date'] == d) & (df['HoldingSharesLevel'].astype(int) >= 15)]
            return subset['percentage'].sum()

        latest_whale_pct = get_whale_pct(latest_date)
        prev_whale_pct = get_whale_pct(prev_date)
        
        diff_whale = latest_whale_pct - prev_whale_pct
        
        score = 0
        reasons = []
        if diff_whale > 0:
            score = 1.0
            reasons.append(f"Whales Buying (+{diff_whale:.2f}%)")
        elif diff_whale < 0:
            score = -1.0
            reasons.append(f"Whales Selling ({diff_whale:.2f}%)")

        return {
            "signal": "BUY" if score > 0 else ("SELL" if score < 0 else "NEUTRAL"),
            "confidence": 0.7 if abs(score) > 0 else 0.5,
            "reason": "; ".join(reasons) if reasons else "No movement",
            "data": {"Whale_Pct": f"{latest_whale_pct:.2f}%", "Change": f"{diff_whale:+.2f}%"}
        }
