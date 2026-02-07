import yaml
import os
from typing import Optional
from models import ServerConfig

class ConfigManager:
    """
    Manages the server configuration stored in a YAML file.
    Provides methods to load, save, and reload configuration dynamically.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Optional[ServerConfig] = None
        self.load()

    def load(self) -> ServerConfig:
        """Loads configuration from the YAML file."""
        if not os.path.exists(self.config_path):
            # Return default config if file doesn't exist
            self.config = ServerConfig(name="Default MCP Server")
            return self.config
            
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f) or {}
            self.config = ServerConfig(**data)
        return self.config

    def save(self, config: ServerConfig):
        """Saves the current configuration to the YAML file."""
        self.config = config
        with open(self.config_path, "w") as f:
            yaml.dump(self.config.dict(), f, sort_keys=False)

    def get_raw_yaml(self) -> str:
        """Returns the raw YAML string for editing in the UI."""
        if not os.path.exists(self.config_path):
            return ""
        with open(self.config_path, "r") as f:
            return f.read()

    def update_from_yaml(self, yaml_content: str):
        """Updates configuration from a raw YAML string."""
        data = yaml.safe_load(yaml_content)
        # Validate with Pydantic
        new_config = ServerConfig(**data)
        self.save(new_config)
        return new_config
