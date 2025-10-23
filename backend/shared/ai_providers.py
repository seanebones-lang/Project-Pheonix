"""
AI Provider abstraction layer for OpenAI, Claude, and Gemini APIs.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
import structlog
import openai
from anthropic import AsyncAnthropic
import google.generativeai as genai

logger = structlog.get_logger()

class AIProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"

class AIProviderManager:
    """Manages AI provider integrations with fallback support."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.primary_provider = AIProvider.OPENAI
        self.fallback_providers = [AIProvider.CLAUDE, AIProvider.GEMINI]
    
    def _initialize_providers(self) -> Dict[AIProvider, Any]:
        """Initialize AI provider clients."""
        providers = {}
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            providers[AIProvider.OPENAI] = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            providers[AIProvider.CLAUDE] = AsyncAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        # Gemini
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            providers[AIProvider.GEMINI] = genai
        
        return providers
    
    async def get_embedding(self, text: str, provider: Optional[AIProvider] = None) -> List[float]:
        """Get text embedding from specified or primary provider."""
        provider = provider or self.primary_provider
        
        try:
            if provider == AIProvider.OPENAI and provider in self.providers:
                return await self._get_openai_embedding(text)
            elif provider == AIProvider.CLAUDE and provider in self.providers:
                return await self._get_claude_embedding(text)
            elif provider == AIProvider.GEMINI and provider in self.providers:
                return await self._get_gemini_embedding(text)
            else:
                raise ValueError(f"Provider {provider} not available")
                
        except Exception as e:
            logger.warning("Primary provider failed, trying fallback", provider=provider, error=str(e))
            return await self._get_embedding_with_fallback(text)
    
    async def _get_embedding_with_fallback(self, text: str) -> List[float]:
        """Try fallback providers for embedding."""
        for provider in self.fallback_providers:
            try:
                if provider in self.providers:
                    return await self.get_embedding(text, provider)
            except Exception as e:
                logger.warning("Fallback provider failed", provider=provider, error=str(e))
                continue
        
        raise RuntimeError("All AI providers failed for embedding")
    
    async def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI."""
        client = self.providers[AIProvider.OPENAI]
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def _get_claude_embedding(self, text: str) -> List[float]:
        """Get embedding from Claude (using text generation as fallback)."""
        # Note: Claude doesn't have direct embedding API, so we use text generation
        client = self.providers[AIProvider.CLAUDE]
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Generate a vector representation for this text: {text}"
            }]
        )
        # This is a simplified approach - in production, you'd want a proper embedding model
        return [0.0] * 1536  # Placeholder
    
    async def _get_gemini_embedding(self, text: str) -> List[float]:
        """Get embedding from Gemini."""
        # Note: Gemini embedding API usage would go here
        # For now, return placeholder
        return [0.0] * 1536  # Placeholder
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        provider: Optional[AIProvider] = None
    ) -> str:
        """Generate text using specified or primary provider."""
        provider = provider or self.primary_provider
        
        try:
            if provider == AIProvider.OPENAI and provider in self.providers:
                return await self._generate_openai_text(prompt, max_tokens, temperature)
            elif provider == AIProvider.CLAUDE and provider in self.providers:
                return await self._generate_claude_text(prompt, max_tokens, temperature)
            elif provider == AIProvider.GEMINI and provider in self.providers:
                return await self._generate_gemini_text(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Provider {provider} not available")
                
        except Exception as e:
            logger.warning("Primary provider failed, trying fallback", provider=provider, error=str(e))
            return await self._generate_text_with_fallback(prompt, max_tokens, temperature)
    
    async def _generate_text_with_fallback(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Try fallback providers for text generation."""
        for provider in self.fallback_providers:
            try:
                if provider in self.providers:
                    return await self.generate_text(prompt, max_tokens, temperature, provider)
            except Exception as e:
                logger.warning("Fallback provider failed", provider=provider, error=str(e))
                continue
        
        raise RuntimeError("All AI providers failed for text generation")
    
    async def _generate_openai_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using OpenAI."""
        client = self.providers[AIProvider.OPENAI]
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def _generate_claude_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Claude."""
        client = self.providers[AIProvider.CLAUDE]
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def _generate_gemini_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text using Gemini."""
        model = self.providers[AIProvider.GEMINI].GenerativeModel('gemini-pro')
        response = await model.generate_content_async(prompt)
        return response.text
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """Generate structured output following a schema."""
        structured_prompt = f"""
        {prompt}
        
        Please respond with valid JSON following this schema:
        {schema}
        
        Ensure the response is valid JSON and follows the schema exactly.
        """
        
        response_text = await self.generate_text(structured_prompt, provider=provider)
        
        try:
            import json
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse structured output", error=str(e), response=response_text)
            raise ValueError(f"Invalid JSON response: {response_text}")
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available AI providers."""
        return list(self.providers.keys())
    
    def set_primary_provider(self, provider: AIProvider) -> bool:
        """Set the primary AI provider."""
        if provider in self.providers:
            self.primary_provider = provider
            logger.info("Primary provider changed", provider=provider)
            return True
        return False