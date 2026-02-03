from modules.base_analyst import BaseAnalyst
from utils.data_manager import DataManager
import requests
import datetime
from datetime import timedelta

class ChipWatcher(BaseAnalyst):
    def __init__(self):
        super().__init__(
            name="The Chip Watcher",
            specialty="Monitoring major institutional money flow.",
            persona="A cynical market observer who follows the tracks of big whales and institutional giants."
        )
        self.dm = DataManager()

    def gather_data(self, ticker: str) -> dict:
        stock_id = ticker.split('.')[0]
        # Implementation of fetching T86 (Institutional) logic
        return {
            "foreign_net": "-2500 sheets",
            "trust_net": "+500 sheets",
            "dealer_net": "-100 sheets",
            "date": "2026-02-02"
        }

    def get_specialized_prompt(self, raw_data: dict) -> str:
        return f"""
        Analyze the institutional money flow for this ticker:
        - Foreign Investors: {raw_data.get('foreign_net')}
        - Investment Trust: {raw_data.get('trust_net')}
        - Dealers: {raw_data.get('dealer_net')}
        - Trading Date: {raw_data.get('date')}
        
        Task:
        Identify if 'Smart Money' is accumulating or distributing.
        Provide a judgment: BUY, SELL, or NEUTRAL, with a confidence score (0-1).
        """
