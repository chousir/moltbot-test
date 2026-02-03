import json
import os
from datetime import datetime

class PaperTrader:
    """
    Virtual Portfolio Manager. 
    Tracks simulated buys, positions, and calculates realized/unrealized PnL.
    """
    def __init__(self, data_dir="/workspaces/moltbot-test/data/portfolio"):
        self.data_dir = data_dir
        self.portfolio_path = os.path.join(self.data_dir, "portfolio.json")
        self.history_path = os.path.join(self.data_dir, "trade_history.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.portfolio_path):
            with open(self.portfolio_path, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "cash": 10000000.0, # Start with 10M TWD
                "positions": {},    # {ticker: {avg_price, quantity, date}}
                "total_equity": 10000000.0
            }
        
        if not os.path.exists(self.history_path):
            self.history = []
        else:
            with open(self.history_path, 'r') as f:
                self.history = json.load(f)

    def _save_state(self):
        with open(self.portfolio_path, 'w') as f:
            json.dump(self.state, f, indent=4)
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f, indent=4)

    def execute_signal(self, ticker, signal, current_price, reason=""):
        """
        Translates Alpha Core signals into virtual trades. 
        Focus: Long-only strategy (No Shorting).
        """
        if signal == "STRONG BUY" or signal == "ACCUMULATE":
            # Simple logic: Invest 10% of available cash per buy signal
            allocation = self.state['cash'] * 0.1
            if allocation < 10000: return # Minimum trade size
            
            quantity = allocation // current_price
            cost = quantity * current_price
            
            if ticker in self.state['positions']:
                pos = self.state['positions'][ticker]
                total_qty = pos['quantity'] + quantity
                total_cost = (pos['avg_price'] * pos['quantity']) + cost
                self.state['positions'][ticker] = {
                    "avg_price": round(total_cost / total_qty, 2),
                    "quantity": total_qty,
                    "last_updated": datetime.now().isoformat()
                }
            else:
                self.state['positions'][ticker] = {
                    "avg_price": current_price,
                    "quantity": quantity,
                    "last_updated": datetime.now().isoformat()
                }
            
            self.state['cash'] -= cost
            self._log_trade("BUY", ticker, quantity, current_price, reason)
            self._save_state()
            return f"Executed BUY {quantity} shares of {ticker} at {current_price}"

        elif signal == "SELL" or signal == "STRONG SELL":
            if ticker in self.state['positions']:
                pos = self.state['positions'][ticker]
                quantity = pos['quantity']
                proceeds = quantity * current_price
                self.state['cash'] += proceeds
                del self.state['positions'][ticker]
                self._log_trade("SELL", ticker, quantity, current_price, reason)
                self._save_state()
                return f"Executed SELL {quantity} shares of {ticker} at {current_price} (Position cleared)"
        
        return "No action taken."

    def _log_trade(self, action, ticker, quantity, price, reason):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "reason": reason
        })

    def update_portfolio_value(self, market_data: dict):
        """
        Updates total equity based on current market prices.
        market_data: {ticker: current_price}
        """
        unrealized_pnl = 0
        total_position_value = 0
        
        for ticker, position in self.state['positions'].items():
            current_price = market_data.get(ticker, position['avg_price'])
            position_value = current_price * position['quantity']
            cost_basis = position['avg_price'] * position['quantity']
            
            unrealized_pnl += (position_value - cost_basis)
            total_position_value += position_value
            
            self.state['positions'][ticker]['current_price'] = current_price
            self.state['positions'][ticker]['unrealized_pnl'] = position_value - cost_basis

        self.state['total_equity'] = self.state['cash'] + total_position_value
        self._save_state()

    def get_summary(self):
        return {
            "Total Equity": f"${self.state['total_equity']:,.2f}",
            "Available Cash": f"${self.state['cash']:,.2f}",
            "Number of Positions": len(self.state['positions']),
            "Current Positions": self.state['positions']
        }
