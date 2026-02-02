import json
import os
import sys
from colorama import Fore, Style, init
from main import AlphaCore
import pandas as pd
import datetime

# Initialize Colorama
init(autoreset=True)

class ChiefAdvisor:
    def __init__(self):
        self.alpha = AlphaCore()
        self.universe_path = "/workspaces/moltbot-test/config/universe.json"
        self.report_date = datetime.datetime.now().strftime("%Y-%m-%d")

    def load_universe(self):
        with open(self.universe_path, 'r') as f:
            return json.load(f)

    def calculate_price_levels(self, ticker, close_price, bbands, report_signal):
        """
        Calculate Target Price and Stop Loss based on Volatility (Bollinger Bands)
        This is a simplified logic. In production, we'd use ATR or Pivot Points.
        """
        try:
            # Extract BBands from Analyst A's hidden data logic or re-calculate?
            # For efficiency, we assume specific fields passed in 'data' or simulate logic here.
            # Since Analyst data structure is generic, we'll do a quick estimation based on price.
            
            # Simple Logic:
            # Target = Current + (Current - LowerBand) * 1.5 (Risk/Reward 1.5)
            # Stop = LowerBand (Support)
            
            # Note: This is a placeholder. Ideally, Chartist should return these levels.
            # Let's define them relative to current price for safety if data missing.
            
            target_price = 0
            stop_loss = 0
            
            if report_signal == "BUY" or report_signal == "STRONG BUY":
                stop_loss = close_price * 0.95 # -5% default tight stop
                target_price = close_price * 1.15 # +15% target
            elif report_signal == "SELL":
                stop_loss = close_price * 1.05
                target_price = close_price * 0.85
            else:
                stop_loss = close_price * 0.90
                target_price = close_price * 1.10

            return round(target_price, 1), round(stop_loss, 1)

        except:
            return 0, 0

    def generate_report(self):
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}=== MoltBot Investment Advisory Report ({self.report_date}) ==={Fore.RESET}")
        
        universe = self.load_universe()
        final_report_md = f"# 📊 MoltBot Investment Advisory Report\n**Date:** {self.report_date}\n\n"
        
        for industry, info in universe.items():
            print(f"\n{Fore.CYAN}>> Analyzing Sector: {industry}{Fore.RESET}")
            final_report_md += f"## 🏭 Sector: {industry}\n*{info['description']}*\n\n"
            final_report_md += "| Ticker | Rating | Close | Target | Stop Loss | Rationale |\n"
            final_report_md += "|---|---|---|---|---|---|\n"

            sector_picks = []

            for ticker in info['tickers']:
                # Run Alpha Analysis (Suppress full output, capture return)
                # We need to modify AlphaCore to return the full dict, not just print.
                # For now, we will capture standard output or modify main.py slightly? 
                # Better: main.py logic is printed. Let's rely on AlphaCore having a method that returns structured data.
                # Since AlphaCore.run_pipeline prints, let's assume we can refactor it slightly 
                # OR we implement a quiet mode in AlphaCore.
                
                # REFACTOR ON THE FLY: 
                # Accessing internal method of AlphaCore isn't clean without refactoring main.py.
                # But I am the builder, so I will assume I can access the analysts directly or refactor main.py.
                # For this script, I will call the logic manually to get the data I need.
                
                reports = []
                final_score = 0
                total_weight = 0
                
                print(f"   Scanning {ticker}...", end="\r")
                
                close_price = 0
                
                for analyst in self.alpha.team:
                    res = analyst.analyze(ticker)
                    res['analyst_name'] = analyst.name
                    reports.append(res)
                    
                    # Capture Close Price from Chartist
                    if analyst.name == "The Chartist (Technical)" and 'Close' in res['data']:
                        close_price = res['data']['Close']

                    # Scoring
                    raw_score = 1 if res['signal'] == "BUY" else (-1 if res['signal'] == "SELL" else 0)
                    weight = self.alpha.weights.get(analyst.name, 0.25)
                    final_score += raw_score * res['confidence'] * weight
                
                # Determine Rating
                rating = "HOLD"
                if final_score > 0.4: rating = "STRONG BUY"
                elif final_score > 0.15: rating = "ACCUMULATE"
                elif final_score < -0.15: rating = "REDUCE"
                elif final_score < -0.4: rating = "SELL"
                
                # Calc Levels
                tp, sl = self.calculate_price_levels(ticker, close_price, None, rating)
                
                # Identify Key Rationale (Top positive/negative reason)
                key_reasons = []
                for r in reports:
                    if r['confidence'] > 0.5:
                        key_reasons.append(f"{r['analyst_name'].split()[1]}: {r['signal']}")
                rationale_str = ", ".join(key_reasons) if key_reasons else "Neutral Outlook"

                # Append to Table
                row = f"| **{ticker}** | {rating} | {close_price} | {tp} | {sl} | {rationale_str} |"
                final_report_md += row + "\n"
                
                print(f"   Processed {ticker}: {rating} (Score: {final_score:.2f})")

                # Classification Logic
                if rating in ["STRONG BUY", "ACCUMULATE"]:
                    sector_picks.append({
                        "ticker": ticker,
                        "rating": rating,
                        "score": final_score
                    })

            # Sector Summary
            if sector_picks:
                final_report_md += "\n**🌟 Top Picks:** " + ", ".join([p['ticker'] for p in sector_picks]) + "\n\n"
            else:
                final_report_md += "\n**⚠️ Sector Warning:** No clear buy signals in this sector.\n\n"

        # Save Report
        with open("/workspaces/moltbot-test/Daily_Report.md", "w") as f:
            f.write(final_report_md)
        
        print(f"\n{Fore.GREEN}Report Generated Successfully: /workspaces/moltbot-test/Daily_Report.md{Fore.RESET}")

if __name__ == "__main__":
    advisor = ChiefAdvisor()
    advisor.generate_report()
