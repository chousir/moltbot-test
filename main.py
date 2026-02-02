import sys
import colorama
from colorama import Fore, Style
import os
import json
from datetime import datetime

# Import analysts
from modules.chartist import Chartist
from modules.valuator import Valuator
from modules.chip_watcher import ChipWatcher
from modules.strategist import Strategist
from modules.whale_hunter import WhaleHunter

# Initialize Colorama
colorama.init(autoreset=True)

class AlphaCore:
    def __init__(self):
        self.team = [
            Chartist(),
            Valuator(),
            ChipWatcher(),
            Strategist(),
            WhaleHunter()
        ]
        
        # Long-Term Investment Weighted Matrix
        self.weights = {
            "The Valuator (Fundamental)": 0.35,
            "The Chip Watcher (Institutional)": 0.25,
            "The Whale Hunter (Large Holders)": 0.20,
            "The Strategist (Macro)": 0.15,
            "The Chartist (Technical)": 0.05
        }

    def run_pipeline(self, ticker: str, save_log: bool = True):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Alpha AI Investment Committee ===")
        print(f"{Fore.CYAN}Target: {ticker}")
        
        # Introduction of the Team
        print(f"{Fore.WHITE}{Style.DIM}Members present: " + ", ".join([m.name for m in self.team]))
        print("-" * 50)

        reports = []
        final_score = 0
        
        for analyst in self.team:
            print(f"{Fore.YELLOW}Consulting {analyst.name}...")
            report = analyst.analyze(ticker)
            report['analyst_name'] = analyst.name
            reports.append(report)
            
            # Logic: Buy=1, Sell=-1, Neutral=0
            raw_val = 1 if report['signal'] == "BUY" else (-1 if report['signal'] == "SELL" else 0)
            weight = self.weights.get(analyst.name, 0.2)
            final_score += raw_val * report['confidence'] * weight

            color = Fore.GREEN if report['signal'] == "BUY" else (Fore.RED if report['signal'] == "SELL" else Fore.YELLOW)
            print(f"   > Opinion: {color}{report['signal']} {Fore.RESET}(Confidence: {report['confidence']:.2f})")
            print(f"   > Rationale: {report['reason']}")

        # Final Decision
        print("-" * 50)
        decision = "HOLD"
        if final_score > 0.4: decision = "STRONG BUY"
        elif final_score > 0.15: decision = "ACCUMULATE"
        elif final_score < -0.4: decision = "STRONG SELL"
        elif final_score < -0.15: decision = "SELL"

        decision_color = Fore.GREEN if "BUY" in decision else (Fore.RED if "SELL" in decision else Fore.YELLOW)
        print(f"Final Committee Score: {final_score:.4f}")
        print(f"Consensus Recommendation: {decision_color}{Style.BRIGHT}{decision}")
        
        if save_log:
            self._save_decision_log(ticker, final_score, decision, reports)

    def _save_decision_log(self, ticker, score, decision, reports):
        log_dir = "/workspaces/moltbot-test/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "score": score,
            "decision": decision,
            "details": reports
        }
        filename = f"{log_dir}/decisions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "2330.TW"
    AlphaCore().run_pipeline(target)
