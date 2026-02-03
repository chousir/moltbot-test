import os
import json
import datetime

class DataManager:
    """
    Handles local data caching to prevent redundant API calls and save tokens/resources.
    Implementation of the 'MCP-lite' concept for data management.
    """
    def __init__(self, cache_dir="/workspaces/moltbot-test/data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_cache_path(self, category, identifier):
        return os.path.join(self.cache_dir, f"{category}_{identifier}.json")

    def save_data(self, category, identifier, data):
        path = self.get_cache_path(category, identifier)
        cache_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data
        }
        with open(path, 'w') as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=4)

    def get_summarized_prompt_data(self, category, identifier, filter_func=None):
        """
        Retrieves data and applies a filtering/summarization function 
        to reduce token count before passing to the LLM.
        """
        data = self.load_data(category, identifier)
        if not data:
            return "No recent data available."
        
        if filter_func:
            return filter_func(data)
        
        # Default: Return a truncated JSON to save tokens
        return json.dumps(data)[:1000] + "... (truncated)"
