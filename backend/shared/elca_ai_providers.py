"""
Enhanced AI Provider with open-source model support and ELCA-specific optimizations.
Supports OpenAI, Claude, Gemini, and Hugging Face models with cost optimization.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import structlog
import openai
from anthropic import AsyncAnthropic
import google.generativeai as genai
from huggingface_hub import AsyncInferenceClient
import httpx

logger = structlog.get_logger()

class AIProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"

class ModelTier(str, Enum):
    PREMIUM = "premium"  # GPT-4, Claude-3.5-Sonnet
    STANDARD = "standard"  # GPT-3.5, Claude-3-Haiku
    OPENSOURCE = "opensource"  # Llama, Mistral via Hugging Face
    EMBEDDING = "embedding"  # Text embeddings

class ELCAAIProviderManager:
    """Enhanced AI provider manager with ELCA-specific optimizations."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.primary_provider = AIProvider.OPENAI
        self.fallback_providers = [AIProvider.CLAUDE, AIProvider.HUGGINGFACE]
        self.cost_optimization_enabled = True
        self.usage_tracking = {}
        
        # ELCA-specific model preferences
        self.elca_model_preferences = {
            "pastoral_care": AIProvider.CLAUDE,  # Better for sensitive conversations
            "worship_planning": AIProvider.OPENAI,  # Good for creative content
            "member_engagement": AIProvider.HUGGINGFACE,  # Cost-effective for routine tasks
            "translation": AIProvider.HUGGINGFACE,  # Open-source models good for i18n
            "general": AIProvider.OPENAI
        }
    
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
        
        # Hugging Face
        if os.getenv("HUGGINGFACE_API_KEY"):
            providers[AIProvider.HUGGINGFACE] = AsyncInferenceClient(
                token=os.getenv("HUGGINGFACE_API_KEY")
            )
        
        return providers
    
    async def get_embedding(self, text: str, provider: Optional[AIProvider] = None) -> List[float]:
        """Get text embedding with cost optimization."""
        provider = provider or AIProvider.OPENAI
        
        try:
            if provider == AIProvider.OPENAI and provider in self.providers:
                return await self._get_openai_embedding(text)
            elif provider == AIProvider.HUGGINGFACE and provider in self.providers:
                return await self._get_huggingface_embedding(text)
            else:
                raise ValueError(f"Provider {provider} not available for embeddings")
                
        except Exception as e:
            logger.warning("Primary embedding provider failed, trying fallback", provider=provider, error=str(e))
            return await self._get_embedding_with_fallback(text)
    
    async def _get_embedding_with_fallback(self, text: str) -> List[float]:
        """Try fallback providers for embedding."""
        for provider in [AIProvider.HUGGINGFACE, AIProvider.OPENAI]:
            try:
                if provider in self.providers:
                    return await self.get_embedding(text, provider)
            except Exception as e:
                logger.warning("Fallback embedding provider failed", provider=provider, error=str(e))
                continue
        
        raise RuntimeError("All embedding providers failed")
    
    async def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI."""
        client = self.providers[AIProvider.OPENAI]
        response = await client.embeddings.create(
            model="text-embedding-3-small",  # Cost-optimized model
            input=text
        )
        return response.data[0].embedding
    
    async def _get_huggingface_embedding(self, text: str) -> List[float]:
        """Get embedding from Hugging Face."""
        client = self.providers[AIProvider.HUGGINGFACE]
        response = await client.feature_extraction(
            model="sentence-transformers/all-MiniLM-L6-v2",
            inputs=text
        )
        return response[0].tolist()
    
    async def generate_text(
        self, 
        prompt: str, 
        use_case: str = "general",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        provider: Optional[AIProvider] = None
    ) -> str:
        """Generate text with ELCA-specific optimizations."""
        
        # Select provider based on use case and cost optimization
        if not provider:
            provider = self._select_optimal_provider(use_case, max_tokens)
        
        try:
            if provider == AIProvider.OPENAI and provider in self.providers:
                return await self._generate_openai_text(prompt, max_tokens, temperature, use_case)
            elif provider == AIProvider.CLAUDE and provider in self.providers:
                return await self._generate_claude_text(prompt, max_tokens, temperature, use_case)
            elif provider == AIProvider.GEMINI and provider in self.providers:
                return await self._generate_gemini_text(prompt, max_tokens, temperature, use_case)
            elif provider == AIProvider.HUGGINGFACE and provider in self.providers:
                return await self._generate_huggingface_text(prompt, max_tokens, temperature, use_case)
            else:
                raise ValueError(f"Provider {provider} not available")
                
        except Exception as e:
            logger.warning("Primary provider failed, trying fallback", provider=provider, error=str(e))
            return await self._generate_text_with_fallback(prompt, use_case, max_tokens, temperature)
    
    def _select_optimal_provider(self, use_case: str, max_tokens: int) -> AIProvider:
        """Select optimal provider based on use case and cost."""
        
        # Use case-specific preferences
        if use_case in self.elca_model_preferences:
            preferred = self.elca_model_preferences[use_case]
            if preferred in self.providers:
                return preferred
        
        # Cost optimization for high-volume tasks
        if max_tokens > 2000 and self.cost_optimization_enabled:
            if AIProvider.HUGGINGFACE in self.providers:
                return AIProvider.HUGGINGFACE
        
        # Default to primary provider
        return self.primary_provider
    
    async def _generate_text_with_fallback(self, prompt: str, use_case: str, max_tokens: int, temperature: float) -> str:
        """Try fallback providers for text generation."""
        for provider in self.fallback_providers:
            try:
                if provider in self.providers:
                    return await self.generate_text(prompt, use_case, max_tokens, temperature, provider)
            except Exception as e:
                logger.warning("Fallback provider failed", provider=provider, error=str(e))
                continue
        
        raise RuntimeError("All text generation providers failed")
    
    async def _generate_openai_text(self, prompt: str, max_tokens: int, temperature: float, use_case: str) -> str:
        """Generate text using OpenAI with ELCA context."""
        client = self.providers[AIProvider.OPENAI]
        
        # Select model based on use case
        model = "gpt-4-turbo-preview" if use_case == "pastoral_care" else "gpt-3.5-turbo"
        
        # Add ELCA context to prompt
        elca_context = self._get_elca_context(use_case)
        enhanced_prompt = f"{elca_context}\n\n{prompt}"
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": enhanced_prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Track usage for cost monitoring
        self._track_usage(AIProvider.OPENAI, model, max_tokens)
        
        return response.choices[0].message.content
    
    async def _generate_claude_text(self, prompt: str, max_tokens: int, temperature: float, use_case: str) -> str:
        """Generate text using Claude with ELCA context."""
        client = self.providers[AIProvider.CLAUDE]
        
        # Select model based on use case
        model = "claude-3-5-sonnet-20241022" if use_case == "pastoral_care" else "claude-3-haiku-20240307"
        
        # Add ELCA context to prompt
        elca_context = self._get_elca_context(use_case)
        enhanced_prompt = f"{elca_context}\n\n{prompt}"
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": enhanced_prompt}]
        )
        
        # Track usage for cost monitoring
        self._track_usage(AIProvider.CLAUDE, model, max_tokens)
        
        return response.content[0].text
    
    async def _generate_gemini_text(self, prompt: str, max_tokens: int, temperature: float, use_case: str) -> str:
        """Generate text using Gemini with ELCA context."""
        model = self.providers[AIProvider.GEMINI].GenerativeModel('gemini-pro')
        
        # Add ELCA context to prompt
        elca_context = self._get_elca_context(use_case)
        enhanced_prompt = f"{elca_context}\n\n{prompt}"
        
        response = await model.generate_content_async(
            enhanced_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        # Track usage for cost monitoring
        self._track_usage(AIProvider.GEMINI, "gemini-pro", max_tokens)
        
        return response.text
    
    async def _generate_huggingface_text(self, prompt: str, max_tokens: int, temperature: float, use_case: str) -> str:
        """Generate text using Hugging Face models with ELCA context."""
        client = self.providers[AIProvider.HUGGINGFACE]
        
        # Select model based on use case
        model = "microsoft/DialoGPT-medium" if use_case == "pastoral_care" else "microsoft/DialoGPT-small"
        
        # Add ELCA context to prompt
        elca_context = self._get_elca_context(use_case)
        enhanced_prompt = f"{elca_context}\n\n{prompt}"
        
        response = await client.text_generation(
            model=model,
            inputs=enhanced_prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            return_full_text=False
        )
        
        # Track usage for cost monitoring
        self._track_usage(AIProvider.HUGGINGFACE, model, max_tokens)
        
        return response[0]["generated_text"]
    
    def _get_elca_context(self, use_case: str) -> str:
        """Get ELCA-specific context for AI prompts."""
        contexts = {
            "pastoral_care": """
            You are assisting with pastoral care in an ELCA congregation. Remember:
            - Ground responses in grace and unconditional love
            - Respect human dignity and worth
            - Encourage professional pastoral care when appropriate
            - Be inclusive and welcoming to all
            - Maintain confidentiality and trust
            """,
            "worship_planning": """
            You are assisting with worship planning in an ELCA congregation. Remember:
            - Honor Lutheran liturgical traditions
            - Include diverse voices and perspectives
            - Ensure accessibility for all abilities
            - Reflect ELCA values of justice and inclusion
            - Support authentic worship experiences
            """,
            "member_engagement": """
            You are assisting with member engagement in an ELCA congregation. Remember:
            - Practice radical hospitality
            - Build authentic community connections
            - Respect diverse backgrounds and experiences
            - Encourage participation and belonging
            - Support spiritual growth and discipleship
            """,
            "general": """
            You are assisting an ELCA congregation. Remember:
            - Ground all responses in ELCA values
            - Practice radical hospitality and inclusion
            - Respect human dignity and worth
            - Support justice and advocacy
            - Honor Lutheran traditions and beliefs
            """
        }
        
        return contexts.get(use_case, contexts["general"])
    
    def _track_usage(self, provider: AIProvider, model: str, tokens: int):
        """Track AI usage for cost monitoring."""
        if provider not in self.usage_tracking:
            self.usage_tracking[provider] = {}
        
        if model not in self.usage_tracking[provider]:
            self.usage_tracking[provider][model] = {"tokens": 0, "requests": 0}
        
        self.usage_tracking[provider][model]["tokens"] += tokens
        self.usage_tracking[provider][model]["requests"] += 1
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        use_case: str = "general",
        provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """Generate structured output following a schema with ELCA context."""
        
        # Add ELCA context to prompt
        elca_context = self._get_elca_context(use_case)
        structured_prompt = f"""
        {elca_context}
        
        {prompt}
        
        Please respond with valid JSON following this schema:
        {schema}
        
        Ensure the response is valid JSON and follows the schema exactly.
        """
        
        response_text = await self.generate_text(structured_prompt, use_case, provider=provider)
        
        try:
            import json
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse structured output", error=str(e), response=response_text)
            raise ValueError(f"Invalid JSON response: {response_text}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics for cost monitoring."""
        total_tokens = 0
        total_requests = 0
        
        for provider, models in self.usage_tracking.items():
            for model, stats in models.items():
                total_tokens += stats["tokens"]
                total_requests += stats["requests"]
        
        return {
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "provider_breakdown": self.usage_tracking,
            "cost_optimization_enabled": self.cost_optimization_enabled
        }
    
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
    
    def enable_cost_optimization(self, enabled: bool = True):
        """Enable or disable cost optimization."""
        self.cost_optimization_enabled = enabled
        logger.info("Cost optimization", enabled=enabled)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all AI providers."""
        health_status = {}
        
        for provider in self.providers:
            try:
                if provider == AIProvider.OPENAI:
                    client = self.providers[provider]
                    await client.models.list()
                    health_status[provider] = "healthy"
                elif provider == AIProvider.CLAUDE:
                    client = self.providers[provider]
                    await client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "test"}]
                    )
                    health_status[provider] = "healthy"
                elif provider == AIProvider.HUGGINGFACE:
                    client = self.providers[provider]
                    await client.text_generation(
                        model="microsoft/DialoGPT-small",
                        inputs="test",
                        max_new_tokens=1
                    )
                    health_status[provider] = "healthy"
                else:
                    health_status[provider] = "healthy"
            except Exception as e:
                health_status[provider] = f"unhealthy: {str(e)}"
        
        return health_status

