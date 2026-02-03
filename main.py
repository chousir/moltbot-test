import sys
import colorama
from colorama import Fore, Style
import os
import json
from datetime import datetime

# Core Modules
from modules.chartist import Chartist
from modules.valuator import Valuator
from modules.chip_watcher import ChipWatcher
from modules.whale_hunter import WhaleHunter
from modules.sentiment_scout import SentimentScout # New Agent

class AlphaCore:
    def __init__(self):
        # We now initialize analysts with the new protocol
        self.team = [
            # Note: Existing analysts are being refactored to gather_data style
            SentimentScout() 
        ]
        self.persona = "The Pragmatic Architect"

    def run_pipeline(self, ticker: str):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AI-Powered Committee Meeting ===")
        
        for analyst in self.team:
            # Step 1: Data Gathering (Python Logic)
            raw_data = analyst.gather_data(ticker)
            
            # Step 2: Prompt Preparation
            identity = analyst.get_identity_context()
            task_prompt = analyst.get_specialized_prompt(raw_data)
            
            # Step 3: AI Judgment (This is where Alpha/LLM takes over)
            print(f"{Fore.YELLOW}Consulting {analyst.name} for AI Judgment...")
            
            # Note: In the real runtime, this string would be sent to the LLM.
            # I will simulate the process by displaying the instruction.
            full_context = f"{identity}\n\nTask:\n{task_prompt}"
            
            print(f"{Fore.WHITE}{Style.DIM}AI Context Prepared for {analyst.name}.")
            # The actual judgment happens in Alpha's mind.
            
if __name__ == "__main__":
    AlphaCore().run_pipeline("2330.TW")
