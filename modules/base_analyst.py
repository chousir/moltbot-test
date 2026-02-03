from abc import ABC, abstractmethod

class BaseAnalyst(ABC):
    """
    Refactored Base Class for AI-Driven Analysts.
    Each analyst now focuses on DATA GATHERING and provides a 
    SPECIALIZED PROMPT for the LLM to perform judgment.
    """
    
    def __init__(self, name: str, specialty: str, persona: str):
        self.name = name
        self.specialty = specialty
        self.persona = persona

    @abstractmethod
    def gather_data(self, ticker: str) -> dict:
        """
        Gathers raw data specific to this analyst's field.
        """
        pass

    @abstractmethod
    def get_specialized_prompt(self, raw_data: dict) -> str:
        """
        Generates the specialized prompt for the LLM to analyze the gathered data.
        """
        pass

    def get_identity_context(self) -> str:
        """
        Returns the persona and specialty context for the LLM.
        """
        return f"You are {self.name}. \nSpecialty: {self.specialty}. \nPersona: {self.persona}."
