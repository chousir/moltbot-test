import yfinance as yf
import pandas_ta as ta
import pandas as pd
from modules.base_analyst import BaseAnalyst

class Chartist(BaseAnalyst):
    def __init__(self):
        super().__init__("The Chartist (Technical)")
        self.specialty = "Decoding price action and market momentum using technical indicators."
        self.persona = "A disciplined trend-follower who believes the chart tells the whole story."

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Analyzing {ticker} price action...")
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty:
                return {"signal": "NEUTRAL", "confidence": 0, "reason": "No data", "data": {}}

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.ta.macd(append=True)
            df.ta.rsi(append=True)
            df.ta.bbands(append=True)
            
            latest = df.iloc[-1]
            rsi = latest['RSI_14']
            
            signal = "NEUTRAL"
            if rsi < 30: signal = "BUY"
            elif rsi > 70: signal = "SELL"

            return {
                "signal": signal,
                "confidence": 0.6,
                "reason": f"RSI is {rsi:.2f}",
                "data": {"RSI": round(rsi, 2), "Close": round(latest['Close'], 2)}
            }
        except Exception as e:
            return {"signal": "NEUTRAL", "confidence": 0, "reason": str(e), "data": {}}
