from modules.base_analyst import BaseAnalyst
from utils.data_manager import DataManager
import pandas as pd

class WhaleHunter(BaseAnalyst):
    def __init__(self):
        super().__init__(
            name="The Whale Hunter",
            specialty="Equity dispersion and large shareholder movement.",
            persona="An expert in ownership structures who detects hidden accumulation by major players."
        )
        self.dm = DataManager()

    def gather_data(self, ticker: str) -> dict:
        stock_id = ticker.split('.')[0]
        # Implementation of fetching FinMind Shareholding data
        return {
            "whale_holding_pct": "72.4%",
            "weekly_change": "+0.45%",
            "retail_holding_pct": "12.1%",
            "retail_change": "-0.2%"
        }

    def get_specialized_prompt(self, raw_data: dict) -> str:
        return f"""
        Analyze the shareholding dispersion data:
        - Whale Holding (>1000 sheets): {raw_data.get('whale_holding_pct')} (Change: {raw_data.get('weekly_change')})
        - Retail Holding (<10 sheets): {raw_data.get('retail_holding_pct')} (Change: {raw_data.get('retail_change')})
        
        Task:
        Determine if the stock ownership is becoming more concentrated or more diluted.
        Provide a judgment: BUY, SELL, or NEUTRAL, with a confidence score (0-1).
        """
