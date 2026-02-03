import json
import os
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

class PerformanceAuditor:
    """
    Analyzes historical decisions and their outcomes to provide insights
    for model and weight adjustments.
    """
    def __init__(self, log_dir="/workspaces/moltbot-test/logs", portfolio_dir="/workspaces/moltbot-test/data/portfolio"):
        self.log_dir = log_dir
        self.portfolio_dir = portfolio_dir

    def run_audit(self, audit_period_days=30):
        """
        Runs a performance audit on decisions made within the specified period.
        """
        print(f"\\n--- Running Performance Audit (Last {audit_period_days} Days) ---")
        
        # 1. Gather all relevant log files
        log_files = self._get_log_files(audit_period_days)
        if not log_files:
            return "No decision logs found for the audit period."

        # 2. Parse decisions and identify reviewable trades
        reviewable_decisions = self._parse_decisions(log_files)
        if not reviewable_decisions:
            return "No 'BUY' decisions found to audit."

        # 3. Fetch current market data for comparison
        tickers = list(reviewable_decisions.keys())
        market_data = self._fetch_market_data(tickers)

        # 4. Generate audit report
        report = self._generate_report(reviewable_decisions, market_data)
        
        return report

    def _get_log_files(self, period_days):
        files = []
        for i in range(period_days + 1):
            date = datetime.now() - timedelta(days=i)
            file_path = os.path.join(self.log_dir, f"decisions_{date.strftime('%Y-%m-%d')}.jsonl")
            if os.path.exists(file_path):
                files.append(file_path)
        return files

    def _parse_decisions(self, log_files):
        decisions = {}
        for file_path in log_files:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line)
                        # We only care about auditing 'BUY' signals
                        if "BUY" in log.get('decision'):
                            ticker = log.get('ticker')
                            if ticker not in decisions:
                                decisions[ticker] = []
                            decisions[ticker].append(log)
                    except json.JSONDecodeError:
                        continue
        return decisions

    def _fetch_market_data(self, tickers):
        if not tickers:
            return {}
        df = yf.download(tickers, period="5d", progress=False)
        # Get the latest close price for each ticker
        latest_prices = df['Close'].iloc[-1].to_dict()
        return latest_prices

    def _generate_report(self, decisions, market_data):
        report_lines = ["\\n## Performance Audit Report\\n"]
        report_lines.append("| Ticker | Decision Date | Decision | Entry Price | Current Price | ROI | Key Contributor |")
        report_lines.append("|---|---|---|---|---|---|---|")

        for ticker, logs in decisions.items():
            for log in logs:
                decision_date = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d')
                
                # Find entry price from the paper trading log (more accurate)
                # This part requires linking with PaperTrader history, for now, we'll estimate from log
                entry_price = self._find_entry_price(ticker, log['timestamp'])
                if not entry_price: continue

                current_price = market_data.get(ticker)
                if not current_price or pd.isna(current_price): continue
                
                roi = ((current_price - entry_price) / entry_price) * 100
                roi_str = f"{roi:+.2f}%"
                
                # AI-powered attribution analysis
                key_contributor = self._attribute_decision(log['details'])

                report_lines.append(f"| {ticker} | {decision_date} | {log['decision']} | {entry_price:.2f} | {current_price:.2f} | {roi_str} | {key_contributor} |")
        
        return "\\n".join(report_lines)

    def _find_entry_price(self, ticker, timestamp_str):
        # In a real scenario, this would query the PaperTrader's trade history
        # to find the exact execution price around the decision timestamp.
        # For now, we simulate this by assuming the price is in the log (which it isn't yet).
        # Let's add a placeholder.
        return 100.0 # Placeholder

    def _attribute_decision(self, analyst_reports):
        """
        Uses LLM reasoning (in spirit) to determine which analyst had the
        most influence on a correct or incorrect decision.
        """
        highest_confidence_analyst = "N/A"
        max_confidence = -1
        
        for report in analyst_reports:
            if "BUY" in report['signal'] and report['confidence'] > max_confidence:
                max_confidence = report['confidence']
                # Get the core name, e.g., "The Valuator"
                highest_confidence_analyst = report['analyst_name'].split('(')[0].strip()

        return highest_confidence_analyst

if __name__ == '__main__':
    auditor = PerformanceAuditor()
    # This is a placeholder for creating dummy log files for testing
    print("PerformanceAuditor module created. Ready for integration and testing.")

