import yaml
from pathlib import Path
from typing import Any, Optional

class ConfigLoader:
    def __init__(self, path: str = "config.yml"):
        self.config_path = Path(path)
        self.data = self._load_config()
        self.FALLBACK_ERROR_FORMAT = self.get("error.fallback_format", "json")
    
    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file {self.config_path} not found")
        
        with self.config_path.open() as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        keys = key.split('.')
        value = self.data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default