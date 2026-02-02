import requests
import pandas as pd
import datetime
from datetime import timedelta
from modules.base_analyst import BaseAnalyst

class WhaleHunter(BaseAnalyst):
    def __init__(self):
        super().__init__("The Whale Hunter (Large Holders)")
        self.api_url = "https://api.finmindtrade.com/api/v4/data"

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Hunting for Whales (Major Shareholders) in {ticker}...")
        
        stock_id = ticker.split('.')[0]
        
        # Determine date range (Last 30 days to cover at least 2-3 weeks of data)
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
        
        params = {
            "dataset": "TaiwanStockShareholding",
            "data_id": stock_id,
            "start_date": start_date,
            "end_date": end_date
        }

        try:
            # FinMind API Call
            resp = requests.get(self.api_url, params=params)
            data = resp.json()
            
            if data['msg'] != 'success' or not data['data']:
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0,
                    "reason": "No Shareholding Data (FinMind)",
                    "data": {}
                }

            df = pd.DataFrame(data['data'])
            
            # Data usually contains: date, stock_id, HoldingSharesLevel (1-17), numberOfShareholders, percentage
            # Level 15: > 1,000,000 shares (1000張) -> The Super Whales
            # We want to see the TREND of Level 15 percentage.
            
            # Filter for Super Whales (>1000 sheets) - usually Level 15 in FinMind structure (needs verification, usually level 15 is max)
            # FinMind levels: 1=1-999, ..., 15=>1000000
            # Let's sum up Level 14 (>800,000) and 15 (>1,000,000) or just look at total huge holders.
            # A simpler proxy is: Look at the rows where 'HoldingSharesLevel' is the highest categories.
            
            # Let's look at specific levels provided by FinMind doc or standard TDCC levels.
            # 15: 1,000,001 up
            
            df['date'] = pd.to_datetime(df['date'])
            latest_date = df['date'].max()
            prev_date = df[df['date'] < latest_date]['date'].max()
            
            if pd.isna(prev_date):
                 return {"signal": "NEUTRAL", "confidence": 0, "reason": "Insufficient history", "data": {}}

            # Extract Whales (>1000 sheets, Level 15)
            # Sometimes data format varies, assuming 'HoldingSharesLevel' column exists.
            
            def get_whale_pct(d):
                # Sum percentage of level 15 (Max)
                # Or levels 14+15 (>800k)
                subset = df[(df['date'] == d) & (df['HoldingSharesLevel'].astype(int) >= 15)]
                return subset['percentage'].sum()

            latest_whale_pct = get_whale_pct(latest_date)
            prev_whale_pct = get_whale_pct(prev_date)
            
            # Extract Retail (<10 sheets, Level 1-2 approx)
            # Level 1: 1-999 shares (<1 sheet)
            # Level 2: 1,000-5,000 shares (1-5 sheets)
            def get_retail_pct(d):
                subset = df[(df['date'] == d) & (df['HoldingSharesLevel'].astype(int) <= 2)]
                return subset['percentage'].sum()

            latest_retail_pct = get_retail_pct(latest_date)
            prev_retail_pct = get_retail_pct(prev_date)

            score = 0
            reasons = []
            
            # 1. Whale Trend
            diff_whale = latest_whale_pct - prev_whale_pct
            if diff_whale > 0.5: # +0.5% in a week is huge
                score += 2.0
                reasons.append(f"Whales Accumulating (+{diff_whale:.2f}%)")
            elif diff_whale > 0:
                score += 1.0
                reasons.append(f"Whales Buying (+{diff_whale:.2f}%)")
            elif diff_whale < -0.5:
                score -= 2.0
                reasons.append(f"Whales Dumping ({diff_whale:.2f}%)")
            elif diff_whale < 0:
                score -= 1.0
                reasons.append(f"Whales Selling ({diff_whale:.2f}%)")

            # 2. Retail Trend (Contra-indicator)
            diff_retail = latest_retail_pct - prev_retail_pct
            if diff_retail < 0:
                score += 0.5 # Good, retail leaving
            elif diff_retail > 0.2:
                score -= 0.5 # Bad, retail entering
                reasons.append("Retail Increasing")

            # 3. Concentration Level
            if latest_whale_pct > 70:
                score += 0.5
                reasons.append(f"Highly Concentrated ({latest_whale_pct:.1f}%)")
            
            # Final Signal
            if score >= 1.5:
                signal = "BUY"
                confidence = 0.8
            elif score <= -1.5:
                signal = "SELL"
                confidence = 0.8
            elif score > 0:
                signal = "BUY" # Weak Buy
                confidence = 0.4
            elif score < 0:
                signal = "SELL" # Weak Sell
                confidence = 0.4
            else:
                signal = "NEUTRAL"
                confidence = 0.5

            return {
                "signal": signal,
                "confidence": confidence,
                "reason": "; ".join(reasons),
                "data": {
                    "Date": latest_date.strftime("%Y-%m-%d"),
                    "Whale_Pct": f"{latest_whale_pct:.2f}%",
                    "Change": f"{diff_whale:+.2f}%"
                }
            }

        except Exception as e:
            return {
                "signal": "NEUTRAL",
                "confidence": 0,
                "reason": f"Whale Error: {str(e)}",
                "data": {}
            }
