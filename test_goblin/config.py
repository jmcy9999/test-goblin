"""Configuration management for iOS Test Optimizer.

Loads thresholds and settings from a JSON configuration file.
Falls back to sensible defaults if no config file is found.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Default thresholds - used when no config file is present
DEFAULT_THRESHOLDS = {
    "test_inventory": {
        "large_file_threshold": 30,
        "description": "Files with more tests trigger 'Split Large Files'",
    },
    "test_file_naming": {
        "pattern": "[Feature]Tests.swift",
        "consistency_threshold": 90.0,
        "description": "Expected file naming pattern and consistency threshold",
    },
    "test_method_naming": {
        "pattern": "camelCase",
        "consistency_threshold": 85.0,
        "description": "Expected method naming style and consistency threshold",
    },
    "accessibility_ids": {
        "generic_id_usage_threshold": 50,
        "centralization_threshold": 50.0,
        "description": "IDs over threshold trigger recommendations",
    },
    "test_plans": {
        "orphaned_tests_threshold": 0,
        "multi_plan_tests_threshold": 0,
        "skipped_tests_threshold": 0,
        "overlap_threshold": 10.0,
        "description": "Thresholds for test plan recommendations",
    },
    "screen_graph": {
        "navigator_adoption_threshold": 80.0,
        "description": "Below this triggers 'Increase Navigator Adoption'",
    },
    "report": {
        "max_items_in_summary": 20,
        "max_items_before_collapse": 50,
        "description": "Controls how many items to show in report sections",
    },
}


class Config:
    """Configuration manager for iOS Test Optimizer."""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls) -> "Config":
        """Singleton pattern - only one config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = DEFAULT_THRESHOLDS.copy()
        return cls._instance

    def load(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from a JSON file.

        Args:
            config_path: Path to config file. If None, searches for:
                1. ./thresholds.json
                2. ./config/thresholds.json
                3. ~/.ios-test-optimizer/thresholds.json
        """
        if config_path is None:
            # Search for config file in standard locations
            search_paths = [
                Path.cwd() / "thresholds.json",
                Path.cwd() / "config" / "thresholds.json",
                Path.home() / ".ios-test-optimizer" / "thresholds.json",
            ]
            for path in search_paths:
                if path.exists():
                    config_path = path
                    break

        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                # Merge user config with defaults (user overrides defaults)
                self._merge_config(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
                print("Using default thresholds.")

    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user configuration with defaults.

        Args:
            user_config: User-provided configuration dictionary
        """
        for section, values in user_config.items():
            if section in self._config and isinstance(values, dict):
                # Update existing section
                for key, value in values.items():
                    if key != "description":  # Don't override descriptions
                        self._config[section][key] = value
            elif section not in ["$schema", "$comment"]:
                # Add new section (but warn about unknown sections)
                self._config[section] = values

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            section: Configuration section (e.g., 'test_inventory')
            key: Configuration key (e.g., 'large_file_threshold')
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        return self._config.get(section, {}).get(key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section.

        Args:
            section: Configuration section name

        Returns:
            Dictionary of configuration values for the section
        """
        section_config: Dict[str, Any] = self._config.get(section, {})
        return section_config

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Get all thresholds as a dictionary."""
        return self._config

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = DEFAULT_THRESHOLDS.copy()


# Convenience functions for module-level access
_config = Config()


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    _config.load(config_path)
    return _config


def get_config() -> Config:
    """Get the current configuration instance.

    Returns:
        Config instance
    """
    return _config


def get_threshold(section: str, key: str, default: Any = None) -> Any:
    """Get a threshold value.

    Args:
        section: Configuration section
        key: Threshold key
        default: Default value

    Returns:
        Threshold value
    """
    return _config.get(section, key, default)
