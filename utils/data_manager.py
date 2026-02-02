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

    def load_data(self, category, identifier, max_age_hours=24):
        path = self.get_cache_path(category, identifier)
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r') as f:
                entry = json.load(f)
            
            # Check age
            timestamp = datetime.datetime.fromisoformat(entry['timestamp'])
            age = datetime.datetime.now() - timestamp
            
            if age.total_seconds() > (max_age_hours * 3600):
                return None # Cache expired
                
            return entry['data']
        except Exception:
            return None
