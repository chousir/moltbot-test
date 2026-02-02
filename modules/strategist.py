import yfinance as yf
from modules.base_analyst import BaseAnalyst

class Strategist(BaseAnalyst):
    def __init__(self):
        super().__init__("The Strategist (Macro)")

    def analyze(self, ticker: str) -> dict:
        print(f"[{self.name}] Scanning Macro Risks (VIX, Bonds)...")
        try:
            # Analyze VIX (Fear Index)
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="5d")
            
            if hist.empty:
                return {"signal": "NEUTRAL", "confidence": 0.0, "reason": "No Macro Data", "data": {}}

            current_vix = hist['Close'].iloc[-1]
            
            reasons = []
            score = 0
            
            if current_vix > 30:
                score -= 2
                reasons.append(f"Extreme Fear (VIX: {current_vix:.2f})")
                signal = "SELL" # Reduce exposure
            elif current_vix > 20:
                score -= 1
                reasons.append(f"High Volatility (VIX: {current_vix:.2f})")
                signal = "NEUTRAL"
            elif current_vix < 15:
                score += 1
                reasons.append(f"Market Calm (VIX: {current_vix:.2f})")
                signal = "BUY" # Good environment for stocks
            else:
                signal = "NEUTRAL"
                reasons.append(f"Normal Volatility (VIX: {current_vix:.2f})")

            return {
                "signal": signal,
                "confidence": abs(score)/2 if score !=0 else 0.5,
                "reason": "; ".join(reasons),
                "data": {"VIX": round(current_vix, 2)}
            }

        except Exception as e:
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "reason": f"Macro Error: {str(e)}",
                "data": {}
            }
