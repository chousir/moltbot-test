from modules.base_analyst import BaseAnalyst
import requests
from bs4 import BeautifulSoup

class SentimentScout(BaseAnalyst):
    def __init__(self):
        super().__init__(
            name="The Sentiment Scout",
            specialty="Market sentiment analysis and news interpretation.",
            persona="A sharp investigative journalist who can read between the lines of financial news."
        )

    def gather_data(self, ticker: str) -> dict:
        """
        Gathers news headlines from major financial portals.
        (Placeholder for real scraping logic, which the Chairman can refine)
        """
        print(f"[{self.name}] Scraping latest headlines for {ticker}...")
        # Simulating news data for AI to judge
        return {
            "headlines": [
                f"{ticker} 營收創歷史新高，展望第二季表現強勁",
                f"外資調高 {ticker} 目標價至新高點",
                f"市場傳聞 {ticker} 供應鏈出現短暫停工",
                f"分析師警告 {ticker} 估值已進入過熱區間"
            ]
        }

    def get_specialized_prompt(self, raw_data: dict) -> str:
        """
        Creates a prompt specifically for semantic sentiment analysis.
        """
        headlines_str = "\n- ".join(raw_data['headlines'])
        return f"""
        Analyze the following news headlines for ticker {self.name}:
        
        Headlines:
        - {headlines_str}
        
        Based on these headlines, judge the market sentiment. 
        Your output must be a structured report in the following format:
        1. SIGNAL: (BUY, SELL, or NEUTRAL)
        2. CONFIDENCE: (0.0 to 1.0)
        3. SUMMARY: (A one-sentence summary of your judgment)
        4. DETAILED_REASONING: (A brief paragraph on why you reached this decision)
        """
