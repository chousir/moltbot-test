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
from modules.strategist import Strategist
from modules.whale_hunter import WhaleHunter
from modules.performance_auditor import PerformanceAuditor

# Utils
from utils.paper_trader import PaperTrader

# Initialize Colorama
colorama.init(autoreset=True)

class AlphaCore:
    """
    Alpha - The Pragmatic Architect.
    The leader of the investment committee. He filters the noise from analysts 
    and builds a structured path to capital growth.
    """
    def __init__(self):
        # The Team
        self.team = [
            Chartist(),
            Valuator(),
            ChipWatcher(),
            Strategist(),
            WhaleHunter()
        ]
        
        # Virtual Account
        self.trader = PaperTrader()
        
        # Performance Auditor - 自我進化引擎
        self.auditor = PerformanceAuditor()

        # Weighted Matrix for Long-term Investing
        self.weights = {
            "The Valuator (Fundamental)": 0.35,
            "The Chip Watcher (Institutional)": 0.25,
            "The Whale Hunter (Large Holders)": 0.20,
            "The Strategist (Macro)": 0.15,
            "The Chartist (Technical)": 0.05
        }
        
        # Alpha's Identity
        self.persona = "The Pragmatic Architect"
        self.motto = "Data has no ego; neither should we."

    def run_pipeline(self, ticker: str, save_log: bool = True, auto_weight_adjust: bool = True):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== {self.persona} Collective Review ===")
        print(f"{Fore.CYAN}Target: {ticker} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 1. 驗證過去的預測（審計引擎）
        self._run_audit_cycle()
        
        # 2. 如果有績效數據，動態調整權重
        if auto_weight_adjust:
            self.weights, was_adjusted = self.auditor.adjust_weights(self.weights)
            if was_adjusted:
                print(f"\n{Fore.YELLOW}[Auto-Adjustment] 權重已根據績效調整:")
                for analyst_name, weight in self.weights.items():
                    print(f"   {analyst_name}: {weight*100:.1f}%")
        
        # 3. 收集分析師意見
        reports = []
        final_score = 0
        current_price = 0
        
        for analyst in self.team:
            print(f"{Fore.YELLOW}Requesting specialized briefing from {analyst.name}...")
            report = analyst.analyze(ticker)
            report['analyst_name'] = analyst.name
            reports.append(report)
            
            # Logic: Buy=1, Sell=-1, Neutral=0
            raw_val = 1 if report['signal'] == "BUY" else (-1 if report['signal'] == "SELL" else 0)
            weight = self.weights.get(analyst.name, 0.2)
            final_score += raw_val * report['confidence'] * weight
            
            # Capture Price
            if 'Close' in report['data']:
                current_price = report['data']['Close']

            color = Fore.GREEN if report['signal'] == "BUY" else (Fore.RED if report['signal'] == "SELL" else Fore.YELLOW)
            print(f"   [{analyst.name}] Opinion: {color}{report['signal']} (Conf: {report['confidence']})")

        # Consensus Decision
        decision = "HOLD"
        if final_score > 0.4: decision = "STRONG BUY"
        elif final_score > 0.15: decision = "ACCUMULATE"
        elif final_score < -0.4: decision = "STRONG SELL"
        elif final_score < -0.15: decision = "SELL"

        # Alpha's Final Verdict
        print("-" * 60)
        decision_color = Fore.GREEN if "BUY" in decision else (Fore.RED if "SELL" in decision else Fore.YELLOW)
        print(f"{Style.BRIGHT}{self.persona}'s Verdict: {decision_color}{decision}")
        print(f"Confidence Score: {final_score:.4f}")

        # Prediction Engine (Short/Medium/Long Term)
        self._generate_predictions(ticker, current_price, final_score)

        # 4. 記錄預測供未來驗證
        if current_price > 0:
            self.auditor.record_prediction(ticker, reports, current_price)

        # Virtual Execution
        if current_price > 0:
            trade_msg = self.trader.execute_signal(ticker, decision, current_price, reason=f"Alpha Score: {final_score:.2f}")
            print(f"{Fore.MAGENTA}[Trading Desk] {trade_msg}")

        if save_log:
            self._save_decision_log(ticker, final_score, decision, reports)

    def _run_audit_cycle(self):
        """執行績效審計周期"""
        try:
            verified_count = self.auditor.verify_predictions()
            if verified_count > 0:
                print(f"\n{Fore.CYAN}[Audit] 已驗證 {verified_count} 個預測")
                # 輸出審計報告摘要
                print(self.auditor.generate_audit_report())
        except Exception as e:
            print(f"{Fore.YELLOW}[Audit] 審計周期發生錯誤: {e}")

    def _generate_predictions(self, ticker, price, score):
        """
        Alpha's Prediction Engine. Estimates price trajectories.
        """
        if price == 0: return
        
        # Calculation is based on score-induced drift
        # This will be replaced by a proper Scikit-learn model in future updates
        print(f"\n{Fore.WHITE}{Style.BRIGHT}--- Projections (Probabilistic Estimates) ---")
        projections = {
            "T+1 (Daily)": price * (1 + (score * 0.01)),
            "T+5 (Weekly)": price * (1 + (score * 0.03)),
            "T+20 (Monthly)": price * (1 + (score * 0.08))
        }
        for period, val in projections.items():
            dir_icon = "📈" if val >= price else "📉"
            print(f"   {period}: {val:.2f} {dir_icon}")

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
