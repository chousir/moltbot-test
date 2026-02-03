import yfinance as yf
import pandas_ta as ta
import pandas as pd
from modules.base_analyst import BaseAnalyst

class Chartist(BaseAnalyst):
    def __init__(self):
        super().__init__(
            name="The Chartist",
            specialty="Price action, momentum, and technical trend analysis.",
            persona="A quantitative technician who interprets charts as the collective psychology of the market."
        )

    def gather_data(self, ticker: str) -> dict:
        """Gathers technical indicators."""
        print(f"[{self.name}] Fetching technical data for {ticker}...")
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty: return {}
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.ta.macd(append=True)
        df.ta.rsi(append=True)
        df.ta.bbands(append=True)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        return {
            "close": round(latest['Close'], 2),
            "rsi": round(latest['RSI_14'], 2),
            "macd": {
                "current": round(latest['MACD_12_26_9'], 2),
                "signal": round(latest['MACDs_12_26_9'], 2),
                "prev_macd": round(prev['MACD_12_26_9'], 2),
                "prev_signal": round(prev['MACDs_12_26_9'], 2)
            },
            "bollinger": {
                "upper": round(latest['BBU_20_2.0'], 2),
                "lower": round(latest['BBL_20_2.0'], 2)
            }
        }

    def get_specialized_prompt(self, raw_data: dict) -> str:
        return f"""
        Review the following technical data for {self.name}:
        - Current Close: {raw_data.get('close')}
        - RSI (14): {raw_data.get('rsi')}
        - MACD: Current Line {raw_data.get('macd', {}).get('current')}, Signal Line {raw_data.get('macd', {}).get('signal')}
        - Bollinger Bands: Upper {raw_data.get('bollinger', {}).get('upper')}, Lower {raw_data.get('bollinger', {}).get('lower')}
        
        Task: 
        As a technical analyst, evaluate the trend, momentum, and volatility. 
        Provide a judgment: BUY, SELL, or NEUTRAL, with a confidence score (0-1).
        """
