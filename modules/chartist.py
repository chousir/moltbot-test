import yfinance as yf
import pandas_ta as ta
import pandas as pd
from modules.base_analyst import BaseAnalyst

class Chartist(BaseAnalyst):
    def __init__(self):
        super().__init__("The Chartist (Technical)")

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Analyzing {ticker} market data...")
        try:
            # Download data (1 year history to ensure enough data for indicators)
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            
            if df.empty:
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0.0,
                    "reason": "No data found",
                    "data": {}
                }

            # Flatten MultiIndex columns if present (yfinance update fix)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate Indicators
            # 1. MACD (12, 26, 9)
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            df = pd.concat([df, macd], axis=1)

            # 2. RSI (14)
            df['RSI'] = df.ta.rsi(length=14)

            # 3. Bollinger Bands
            bbands = df.ta.bbands(length=20, std=2)
            df = pd.concat([df, bbands], axis=1)
            
            # DEBUG: Print columns to identify correct names if error occurs
            # print(df.columns) 

            # Identify BBL/BBU column names dynamically
            bbl_col = [c for c in df.columns if c.startswith('BBL')][0]
            bbu_col = [c for c in df.columns if c.startswith('BBU')][0]

            # Get latest row
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            signal = "NEUTRAL"
            score = 0
            reasons = []

            # Strategy Logic
            
            # RSI Logic
            rsi = latest['RSI']
            if rsi < 30:
                score += 1
                reasons.append(f"RSI Oversold ({rsi:.2f})")
            elif rsi > 70:
                score -= 1
                reasons.append(f"RSI Overbought ({rsi:.2f})")
            
            # MACD Logic (Golden Cross)
            macd_col = [c for c in df.columns if c.startswith('MACD_')][0]
            macds_col = [c for c in df.columns if c.startswith('MACDs_')][0]

            macd_line = latest[macd_col]
            signal_line = latest[macds_col]
            prev_macd = prev[macd_col]
            prev_signal = prev[macds_col]

            if macd_line > signal_line and prev_macd <= prev_signal:
                score += 2
                reasons.append("MACD Golden Cross")
            elif macd_line < signal_line and prev_macd >= prev_signal:
                score -= 2
                reasons.append("MACD Death Cross")
            elif macd_line > signal_line:
                score += 0.5 # Bullish trend holding
            elif macd_line < signal_line:
                score -= 0.5 # Bearish trend holding

            # Price relative to BBands
            close_price = latest['Close']
            if close_price < latest[bbl_col]:
                score += 1
                reasons.append("Price below Lower Bollinger Band")
            elif close_price > latest[bbu_col]:
                score -= 1
                reasons.append("Price above Upper Bollinger Band")

            # Final Decision
            if score >= 1.5:
                signal = "BUY"
                confidence = min(abs(score) / 4, 1.0) # Normalize cap
            elif score <= -1.5:
                signal = "SELL"
                confidence = min(abs(score) / 4, 1.0)
            else:
                signal = "NEUTRAL"
                confidence = 0.5

            return {
                "signal": signal,
                "confidence": round(confidence, 2),
                "reason": "; ".join(reasons) if reasons else "Market Choppy",
                "data": {
                    "RSI": round(rsi, 2),
                    "Close": round(close_price, 2),
                    "MACD_Cross": "Yes" if "Cross" in "; ".join(reasons) else "No"
                }
            }

        except Exception as e:
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": f"Error: {str(e)}",
                "data": {}
            }
