"""
AI Provider Configuration Module

This module provides centralized configuration for AI providers,
supporting both Anthropic and Gemini models based on environment variables.
Supports per-agent model configuration for optimal task-specific performance.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.language_models import BaseLanguageModel

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


class AIProviderConfig:
    """Configuration class for AI providers with per-agent support"""
    
    def __init__(self):
        # Global defaults
        self.default_ai_provider = os.getenv("AI_PROVIDER", "anthropic").lower()
        self.default_model_name = os.getenv("MODEL_NAME", self._get_default_model_for_provider(self.default_ai_provider))
        self.default_max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        
        # Validate default AI_PROVIDER value
        if self.default_ai_provider not in ["anthropic", "gemini"]:
            raise ValueError(f"Unsupported AI_PROVIDER: {self.default_ai_provider}. Supported values: 'anthropic', 'gemini'")
    
    def _get_default_model_for_provider(self, provider: str) -> str:
        """Get default model name for a provider"""
        defaults = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-pro"
        }
        return defaults.get(provider, "claude-3-5-sonnet-20241022")
    
    def get_llm(
        self, 
        agent_name: Optional[str] = None,
        temperature: float = 0, 
        max_tokens: Optional[int] = None
    ) -> BaseLanguageModel:
        """
        Get the configured LLM instance for a specific agent or use global defaults.
        
        Args:
            agent_name: Name of the agent (e.g., 'AUTHENTICATION', 'FLOW_BUILDER')
            temperature: Temperature for the model (default: 0)
            max_tokens: Maximum tokens for the model (default: uses agent-specific or global MAX_TOKENS)
            
        Returns:
            Configured LLM instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Get agent-specific configuration or fall back to defaults
        ai_provider = self._get_agent_config(agent_name, "AI_PROVIDER", self.default_ai_provider).lower()
        model_name = self._get_agent_config(agent_name, "MODEL_NAME", self.default_model_name)
        
        if max_tokens is None:
            max_tokens = int(self._get_agent_config(agent_name, "MAX_TOKENS", self.default_max_tokens))
            
        if ai_provider == "anthropic":
            return self._get_anthropic_llm(agent_name, model_name, temperature, max_tokens)
        elif ai_provider == "gemini":
            return self._get_gemini_llm(agent_name, model_name, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported AI provider for {agent_name or 'global'}: {ai_provider}")
    
    def _get_agent_config(self, agent_name: Optional[str], config_key: str, default_value: Any) -> Any:
        """
        Get agent-specific configuration or fall back to global default.
        
        Agent-specific env vars follow pattern: {AGENT_NAME}_{CONFIG_KEY}
        Example: FLOW_BUILDER_AI_PROVIDER, AUTHENTICATION_MODEL_NAME, TEST_DESIGNER_MAX_TOKENS
        """
        if agent_name:
            agent_specific_key = f"{agent_name.upper()}_{config_key}"
            agent_value = os.getenv(agent_specific_key)
            if agent_value is not None:
                return agent_value
        
        # Fall back to global config
        return os.getenv(config_key, default_value)
    
    def _get_anthropic_llm(self, agent_name: Optional[str], model_name: str, temperature: float, max_tokens: int) -> BaseLanguageModel:
        """Get Anthropic LLM instance with agent-specific configuration"""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic is required for Anthropic provider. Install it with: pip install langchain-anthropic")
        
        # Check for agent-specific API key first, then global
        api_key = self._get_agent_config(agent_name, "ANTHROPIC_API_KEY", None)
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(f"ANTHROPIC_API_KEY not found for {agent_name or 'global'} configuration.")
        
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            anthropic_api_key=api_key
        )
    
    def _get_gemini_llm(self, agent_name: Optional[str], model_name: str, temperature: float, max_tokens: int) -> BaseLanguageModel:
        """Get Gemini LLM instance with agent-specific configuration"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("langchain-google-genai is required for Gemini provider. Install it with: pip install langchain-google-genai")
        
        # Check for agent-specific API key first, then global
        api_key = self._get_agent_config(agent_name, "GEMINI_API_KEY", None)
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(f"GEMINI_API_KEY not found for {agent_name or 'global'} configuration.")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key
        )
    
    def get_provider_info(self, agent_name: Optional[str] = None) -> dict:
        """Get information about the provider configuration for a specific agent"""
        ai_provider = self._get_agent_config(agent_name, "AI_PROVIDER", self.default_ai_provider).lower()
        model_name = self._get_agent_config(agent_name, "MODEL_NAME", self.default_model_name)
        max_tokens = int(self._get_agent_config(agent_name, "MAX_TOKENS", self.default_max_tokens))
        
        # Check if API key is available for the provider
        if ai_provider == "anthropic":
            api_key_set = bool(
                self._get_agent_config(agent_name, "ANTHROPIC_API_KEY", None) or 
                os.getenv("ANTHROPIC_API_KEY")
            )
        elif ai_provider == "gemini":
            api_key_set = bool(
                self._get_agent_config(agent_name, "GEMINI_API_KEY", None) or 
                os.getenv("GEMINI_API_KEY")
            )
        else:
            api_key_set = False
        
        return {
            "agent": agent_name or "global",
            "provider": ai_provider,
            "model": model_name,
            "api_key_set": api_key_set,
            "max_tokens": max_tokens
        }
    
    def get_all_agent_configs(self) -> Dict[str, dict]:
        """Get configuration information for all detected agent configurations"""
        configs = {"global": self.get_provider_info()}
        
        # Common agent names to check for specific configurations
        agent_names = [
            "AUTHENTICATION",
            "FLOW_BUILDER", 
            "DEPLOYMENT",
            "WEB_SEARCH",
            "TEST_DESIGNER",
            "FLOW_VALIDATION",
            "TEST_EXECUTOR",
            "FLOW_TEST"
        ]
        
        for agent_name in agent_names:
            # Check if agent has any specific configuration
            has_specific_config = any([
                os.getenv(f"{agent_name}_AI_PROVIDER"),
                os.getenv(f"{agent_name}_MODEL_NAME"),
                os.getenv(f"{agent_name}_MAX_TOKENS"),
                os.getenv(f"{agent_name}_ANTHROPIC_API_KEY"),
                os.getenv(f"{agent_name}_GEMINI_API_KEY")
            ])
            
            if has_specific_config:
                configs[agent_name.lower()] = self.get_provider_info(agent_name)
        
        return configs


# Global configuration instance
ai_config = AIProviderConfig()


def get_llm(
    agent_name: Optional[str] = None,
    temperature: float = 0, 
    max_tokens: Optional[int] = None
) -> BaseLanguageModel:
    """
    Convenience function to get the configured LLM instance for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'AUTHENTICATION', 'FLOW_BUILDER')
        temperature: Temperature for the model (default: 0)
        max_tokens: Maximum tokens for the model (default: uses agent-specific or global config)
        
    Returns:
        Configured LLM instance
        
    Example:
        # Use global configuration
        llm = get_llm()
        
        # Use agent-specific configuration
        auth_llm = get_llm("AUTHENTICATION")
        flow_llm = get_llm("FLOW_BUILDER", temperature=0.1)
    """
    return ai_config.get_llm(agent_name=agent_name, temperature=temperature, max_tokens=max_tokens)


def get_provider_info(agent_name: Optional[str] = None) -> dict:
    """
    Convenience function to get provider information for a specific agent.
    
    Args:
        agent_name: Name of the agent (optional, defaults to global config)
        
    Returns:
        Dictionary with provider configuration details
    """
    return ai_config.get_provider_info(agent_name)


def get_all_agent_configs() -> Dict[str, dict]:
    """
    Convenience function to get all agent configurations.
    
    Returns:
        Dictionary mapping agent names to their configurations
    """
    return ai_config.get_all_agent_configs() 