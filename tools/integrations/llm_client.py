"""
Cliente unificado para múltiplos provedores de LLM.
Suporta OpenAI, Google Gemini e Groq.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Provedores de LLM suportados."""
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"


@dataclass
class LLMMessage:
    """Mensagem para o LLM."""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Resposta do LLM."""
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMClient:
    """Cliente unificado para múltiplos provedores de LLM."""
    
    def __init__(
        self,
        provider: Union[str, LLMProvider] = LLMProvider.OPENAI,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializar cliente LLM.
        
        Args:
            provider: Provedor de LLM (openai, gemini, groq)
            model: Nome do modelo específico
            api_key: Chave da API (opcional, usa variável de ambiente)
            **kwargs: Parâmetros específicos do provedor
        """
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())
        
        self.provider = provider
        self.model = model or self._get_default_model()
        self.api_key = api_key or self._get_api_key()
        self.kwargs = kwargs
        
        # Cliente específico do provedor
        self._client = None
        self._initialize_client()
    
    def _get_default_model(self) -> str:
        """Obter modelo padrão para cada provedor."""
        defaults = {
            LLMProvider.OPENAI: "gpt-3.5-turbo",
            LLMProvider.GEMINI: "gemini-pro",
            LLMProvider.GROQ: "llama2-70b-4096"
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")
    
    def _get_api_key(self) -> Optional[str]:
        """Obter chave da API das variáveis de ambiente."""
        env_vars = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.GEMINI: "GOOGLE_API_KEY",
            LLMProvider.GROQ: "GROQ_API_KEY"
        }
        env_var = env_vars.get(self.provider)
        return os.getenv(env_var) if env_var else None
    
    def _initialize_client(self):
        """Inicializar cliente específico do provedor."""
        try:
            if self.provider == LLMProvider.OPENAI:
                self._initialize_openai()
            elif self.provider == LLMProvider.GEMINI:
                self._initialize_gemini()
            elif self.provider == LLMProvider.GROQ:
                self._initialize_groq()
        except ImportError as e:
            logger.warning(f"Dependências não instaladas para {self.provider.value}: {e}")
            self._client = None
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente {self.provider.value}: {e}")
            self._client = None
    
    def _initialize_openai(self):
        """Inicializar cliente OpenAI."""
        try:
            import openai
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                **self.kwargs
            )
        except ImportError:
            raise ImportError(
                "OpenAI dependencies not installed. Run: pip install openai"
            )
    
    def _initialize_gemini(self):
        """Inicializar cliente Google Gemini."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError(
                "Google Gemini dependencies not installed. Run: pip install google-generativeai"
            )
    
    def _initialize_groq(self):
        """Inicializar cliente Groq."""
        try:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Groq dependencies not installed. Run: pip install groq"
            )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Gerar resposta usando o LLM.
        
        Args:
            messages: Lista de mensagens
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            Resposta do LLM
        """
        if not self._client:
            raise RuntimeError(f"Cliente {self.provider.value} não inicializado")
        
        try:
            if self.provider == LLMProvider.OPENAI:
                return await self._generate_openai(messages, temperature, max_tokens, **kwargs)
            elif self.provider == LLMProvider.GEMINI:
                return await self._generate_gemini(messages, temperature, max_tokens, **kwargs)
            elif self.provider == LLMProvider.GROQ:
                return await self._generate_groq(messages, temperature, max_tokens, **kwargs)
            else:
                raise ValueError(f"Provedor não suportado: {self.provider}")
        except Exception as e:
            logger.error(f"Erro na geração {self.provider.value}: {e}")
            raise
    
    async def _generate_openai(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Gerar resposta usando OpenAI."""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        response = await self._client.chat.completions.create(**params)  # type: ignore
        
        return LLMResponse(
            content=response.choices[0].message.content,
            provider=self.provider.value,
            model=self.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        )
    
    async def _generate_gemini(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Gerar resposta usando Google Gemini."""
        # Gemini usa formato diferente - combinar mensagens em prompt
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Configurar parâmetros de geração
        generation_config = {
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Gerar resposta (executar em thread pois Gemini não é async nativo)
        def _generate():
            return self._client.generate_content(  # type: ignore
                prompt,
                generation_config=generation_config
            )
        
        response = await asyncio.get_event_loop().run_in_executor(
            None, _generate
        )
        
        return LLMResponse(
            content=response.text,
            provider=self.provider.value,
            model=self.model,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else None,
                "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else None,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else None
            } if hasattr(response, 'usage_metadata') and response.usage_metadata else None
        )
    
    async def _generate_groq(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Gerar resposta usando Groq."""
        groq_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        params = {
            "model": self.model,
            "messages": groq_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        response = await self._client.chat.completions.create(**params)  # type: ignore
        
        return LLMResponse(
            content=response.choices[0].message.content,
            provider=self.provider.value,
            model=self.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None
        )
    
    def is_available(self) -> bool:
        """Verificar se o cliente está disponível."""
        return self._client is not None and self.api_key is not None


class MockLLMClient:
    """Cliente LLM mock para desenvolvimento."""
    
    def __init__(self, provider: str = "mock", model: str = "mock-model"):
        self.provider = provider
        self.model = model
    
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Gerar resposta mock."""
        # Resposta baseada na última mensagem
        last_message = messages[-1].content.lower() if messages else ""
        
        # Respostas específicas para diferentes tipos de solicitação
        if "agendar" in last_message or "agendamento" in last_message:
            content = "Entendi que você quer fazer um agendamento. Vou processar isso para você."
        elif "disponibilidade" in last_message or "horário" in last_message:
            content = "Vou verificar a disponibilidade de horários para você."
        elif "cancelar" in last_message:
            content = "Vou cancelar o agendamento solicitado."
        elif "listar" in last_message:
            content = "Vou listar os agendamentos para você."
        else:
            content = f"Recebi sua mensagem e vou processar: {last_message[:100]}..."
        
        return LLMResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            usage={"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
        )
    
    def is_available(self) -> bool:
        """Cliente mock sempre disponível."""
        return True


def create_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    use_mock: bool = False,
    **kwargs
) -> Union[LLMClient, MockLLMClient]:
    """
    Factory para criar cliente LLM.
    
    Args:
        provider: Provedor (openai, gemini, groq)
        model: Modelo específico
        api_key: Chave da API
        use_mock: Usar cliente mock
        **kwargs: Parâmetros específicos
        
    Returns:
        Cliente LLM configurado
    """
    if use_mock:
        return MockLLMClient(provider or "mock", model or "mock-model")
    
    # Tentar auto-detectar provedor baseado nas variáveis de ambiente
    if not provider:
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("GOOGLE_API_KEY"):
            provider = "gemini"
        elif os.getenv("GROQ_API_KEY"):
            provider = "groq"
        else:
            logger.warning("Nenhuma chave de API encontrada, usando cliente mock")
            return MockLLMClient()
    
    try:
        return LLMClient(provider, model, api_key, **kwargs)
    except Exception as e:
        logger.warning(f"Erro ao criar cliente {provider}, usando mock: {e}")
        return MockLLMClient(provider or "mock", model or "mock-model")


# Exemplos de uso
if __name__ == "__main__":
    async def test_llm_clients():
        """Testar diferentes clientes LLM."""
        
        # Mensagens de teste
        messages = [
            LLMMessage("system", "Você é um assistente útil para agendamentos."),
            LLMMessage("user", "Quero agendar um corte de cabelo para amanhã às 15:00")
        ]
        
        # Testar diferentes provedores
        providers = ["openai", "gemini", "groq"]
        
        for provider in providers:
            print(f"\n🧠 Testando {provider.upper()}...")
            
            try:
                client = create_llm_client(provider=provider)
                
                if client.is_available():
                    response = await client.generate(messages)
                    print(f"✅ Resposta: {response.content[:100]}...")
                    print(f"📊 Uso: {response.usage}")
                else:
                    print(f"❌ Cliente {provider} não disponível")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Testar cliente mock
        print(f"\n🎭 Testando cliente MOCK...")
        mock_client = create_llm_client(use_mock=True)
        response = await mock_client.generate(messages)
        print(f"✅ Resposta Mock: {response.content}")
    
    # Executar testes
    asyncio.run(test_llm_clients())
