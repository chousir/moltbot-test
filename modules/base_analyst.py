from abc import ABC, abstractmethod

class BaseAnalyst(ABC):
    """
    Abstract Base Class for all Virtual Analysts.
    Ensures every analyst speaks the same language (returns a standard report).
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def analyze(self, ticker: str) -> dict:
        """
        Perform analysis on the given ticker.
        
        Returns:
            dict: {
                "signal": "BUY" | "SELL" | "NEUTRAL",
                "confidence": float (0.0 - 1.0),
                "reason": str,
                "data": dict (raw data used for decision)
            }
        """
        pass
