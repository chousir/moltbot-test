import sys
import colorama
from colorama import Fore, Style
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
        
        # Weighted Decision Matrix (Long-Term Investment Strategy)
        # Fundamental & Institutional are key for long-term holding.
        # Technical is only for entry timing (low weight).
        self.weights = {
            "The Valuator (Fundamental)": 0.35,       # Core Value
            "The Chip Watcher (Institutional)": 0.25, # Smart Money Flow (Daily)
            "The Whale Hunter (Large Holders)": 0.20, # Deep Pockets (Weekly)
            "The Strategist (Macro)": 0.15,           # Market Risk
            "The Chartist (Technical)": 0.05          # Timing Optimization
        }

    def run_pipeline(self, ticker: str, save_log: bool = True):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Alpha AI System Initialized (Long-Term Focus) ===")
        print(f"{Fore.CYAN}Target: {ticker}\n")

        reports = []
        final_score = 0
        total_weight = 0

        # 1. Gather Intelligence
        for analyst in self.team:
            report = analyst.analyze(ticker)
            report['analyst_name'] = analyst.name
            reports.append(report)
            
            # 2. Scoring Mechanism
            # BUY = 1, SELL = -1, NEUTRAL = 0
            raw_score = 0
            if report['signal'] == "BUY":
                raw_score = 1
            elif report['signal'] == "SELL":
                raw_score = -1
            
            # Weighted Score
            weight = self.weights.get(analyst.name, 0.25)
            weighted_score = raw_score * report['confidence'] * weight
            
            final_score += weighted_score
            total_weight += weight

            # Print Analyst Report
            color = Fore.GREEN if report['signal'] == "BUY" else (Fore.RED if report['signal'] == "SELL" else Fore.YELLOW)
            print(f"{Fore.WHITE}[{analyst.name}] -> {color}{report['signal']} {Fore.RESET}(Conf: {report['confidence']:.2f})")
            print(f"   Reason: {report['reason']}")
            print(f"   Data: {report['data']}")
            print("-" * 40)

        # 3. Final Decision Logic
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== FINAL DECISION REPORT ===")
        print(f"Composite Score: {final_score:.4f} (Range: -1.0 to 1.0)")
        
        decision = "HOLD / WATCH"
        action_color = Fore.YELLOW
        
        if final_score > 0.5: # Higher threshold for Long-Term Buy
            decision = "STRONG BUY (Long-Term)"
            action_color = Fore.GREEN
        elif final_score > 0.2:
            decision = "ACCUMULATE (Buy on Dip)"
            action_color = Fore.LIGHTGREEN_EX
        elif final_score < -0.4:
            decision = "SELL / EXIT"
            action_color = Fore.RED
        elif final_score < -0.15:
            decision = "REDUCE POSITIONS"
            action_color = Fore.LIGHTRED_EX

        print(f"Recommendation: {action_color}{Style.BRIGHT}{decision}")
        print("=" * 40)
        
        # 4. Save Log for Self-Reflection
        if save_log:
            self._save_decision_log(ticker, final_score, decision, reports)

    def _save_decision_log(self, ticker, score, decision, reports):
        import json
        import os
        from datetime import datetime
        
        log_dir = "/workspaces/moltbot-test/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "final_score": score,
            "decision": decision,
            "details": reports
        }
        
        # Daily Log File
        filename = f"{log_dir}/decisions_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        print(f"{Fore.LIGHTBLACK_EX}[System] Decision saved to {filename} for future review.")

if __name__ == "__main__":
    target = "2330.TW" 
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    alpha = AlphaCore()
    alpha.run_pipeline(target)
