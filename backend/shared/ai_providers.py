"""
AI Provider abstraction layer for OpenAI, Claude, and Gemini APIs.
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum

import openai
import anthropic
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class AIProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"

class AIProviderError(Exception):
    """Custom exception for AI provider errors."""
    pass

class AIProviderBase(ABC):
    """Base class for AI providers."""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate text response from the AI provider."""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON response."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for the given text."""
        pass

class OpenAIProvider(AIProviderBase):
    """OpenAI API provider implementation."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        super().__init__(api_key or OPENAI_API_KEY, model)
        if not self.api_key:
            raise AIProviderError("OpenAI API key not provided")
        
        self._client = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=self.model,
            temperature=0.1,
            max_tokens=4000
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate text using OpenAI."""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = await self._client.agenerate([messages])
            return response.generations[0][0].text
        except Exception as e:
            raise AIProviderError(f"OpenAI API error: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON using OpenAI."""
        try:
            system_prompt = f"""You are a helpful assistant that generates structured JSON responses.
            Always respond with valid JSON that matches this schema: {json.dumps(schema, indent=2)}
            Do not include any text outside the JSON response."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self._client.agenerate([messages])
            result = response.generations[0][0].text
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end != 0:
                    return json.loads(result[start:end])
                raise AIProviderError("Failed to parse JSON response")
                
        except Exception as e:
            raise AIProviderError(f"OpenAI structured generation error: {str(e)}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise AIProviderError(f"OpenAI embeddings error: {str(e)}")

class ClaudeProvider(AIProviderBase):
    """Claude API provider implementation."""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key or CLAUDE_API_KEY, model)
        if not self.api_key:
            raise AIProviderError("Claude API key not provided")
        
        self._client = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model_name=self.model,
            temperature=0.1,
            max_tokens=4000
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate text using Claude."""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = await self._client.agenerate([messages])
            return response.generations[0][0].text
        except Exception as e:
            raise AIProviderError(f"Claude API error: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON using Claude."""
        try:
            system_prompt = f"""You are a helpful assistant that generates structured JSON responses.
            Always respond with valid JSON that matches this schema: {json.dumps(schema, indent=2)}
            Do not include any text outside the JSON response."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self._client.agenerate([messages])
            result = response.generations[0][0].text
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end != 0:
                    return json.loads(result[start:end])
                raise AIProviderError("Failed to parse JSON response")
                
        except Exception as e:
            raise AIProviderError(f"Claude structured generation error: {str(e)}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Claude doesn't have embeddings API, use OpenAI as fallback."""
        openai_provider = OpenAIProvider()
        return await openai_provider.generate_embeddings(text)

class AIProviderManager:
    """Manager for AI providers with fallback support."""
    
    def __init__(self):
        self.providers: Dict[AIProvider, AIProviderBase] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers."""
        try:
            if OPENAI_API_KEY:
                self.providers[AIProvider.OPENAI] = OpenAIProvider()
        except AIProviderError:
            pass
        
        try:
            if CLAUDE_API_KEY:
                self.providers[AIProvider.CLAUDE] = ClaudeProvider()
        except AIProviderError:
            pass
    
    def get_provider(self, provider: AIProvider = None) -> AIProviderBase:
        """Get AI provider with fallback logic."""
        if provider and provider in self.providers:
            return self.providers[provider]
        
        # Fallback to first available provider
        for provider_instance in self.providers.values():
            return provider_instance
        
        raise AIProviderError("No AI providers available")
    
    async def generate_text(self, prompt: str, system_prompt: str = None, provider: AIProvider = None, **kwargs) -> str:
        """Generate text with fallback support."""
        try:
            provider_instance = self.get_provider(provider)
            return await provider_instance.generate_text(prompt, system_prompt, **kwargs)
        except AIProviderError as e:
            # Try fallback providers
            for fallback_provider in self.providers.values():
                if fallback_provider != provider_instance:
                    try:
                        return await fallback_provider.generate_text(prompt, system_prompt, **kwargs)
                    except AIProviderError:
                        continue
            raise e
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], provider: AIProvider = None, **kwargs) -> Dict[str, Any]:
        """Generate structured response with fallback support."""
        try:
            provider_instance = self.get_provider(provider)
            return await provider_instance.generate_structured(prompt, schema, **kwargs)
        except AIProviderError as e:
            # Try fallback providers
            for fallback_provider in self.providers.values():
                if fallback_provider != provider_instance:
                    try:
                        return await fallback_provider.generate_structured(prompt, schema, **kwargs)
                    except AIProviderError:
                        continue
            raise e
    
    async def generate_embeddings(self, text: str, provider: AIProvider = None) -> List[float]:
        """Generate embeddings with fallback support."""
        try:
            provider_instance = self.get_provider(provider)
            return await provider_instance.generate_embeddings(text)
        except AIProviderError as e:
            # Try fallback providers
            for fallback_provider in self.providers.values():
                if fallback_provider != provider_instance:
                    try:
                        return await fallback_provider.generate_embeddings(text)
                    except AIProviderError:
                        continue
            raise e

# Global instance
ai_manager = AIProviderManager()
