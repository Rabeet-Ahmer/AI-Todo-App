"""
Agent configuration module

Handles loading configuration for AI agents using Gemini API via OpenAI compatibility layer
"""

import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """Configuration for AI agents using Gemini API"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"  # Default Gemini model for agents

    # Agent Behavior Configuration
    max_turns: int = 10  # Maximum conversation turns per session
    default_temperature: float = 0.7

    # Session Configuration
    session_db_path: str = ".agent-sessions/conversations.db"
    session_timeout_hours: int = 24

    # Rate Limiting
    rate_limit_requests_per_minute: int = 30


# Global config instance
config = AgentConfig()


def get_agent_config() -> AgentConfig:
    """Get the global agent configuration"""
    return config
