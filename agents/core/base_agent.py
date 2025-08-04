"""
Base Agent

Classe base para todos os agents do sistema.
Define a interface comum e funcionalidades básicas.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class AgentMessage:
    """Estrutura para mensagens entre agents."""
    sender: str
    recipient: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """
    Classe base para todos os agents.
    
    Define a interface comum que todos os agents devem implementar
    e fornece funcionalidades básicas como logging e comunicação.
    """
    
    def __init__(
        self, 
        name: str, 
        model_client=None, 
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        use_mock_llm: bool = False,
        **kwargs
    ):
        """
        Inicializa o agent base.
        
        Args:
            name: Nome único do agent
            model_client: Cliente do modelo LLM (opcional, para compatibilidade)
            llm_provider: Provedor de LLM (openai, gemini, groq)
            llm_model: Modelo específico do LLM
            llm_api_key: Chave da API do LLM
            use_mock_llm: Usar cliente LLM mock
            **kwargs: Argumentos adicionais específicos do agent
        """
        self.name = name
        self.model_client = model_client  # Mantido para compatibilidade
        self.logger = self._setup_logger()
        self.created_at = datetime.now()
        self.message_history: List[AgentMessage] = []
        self.config = kwargs
        
        # Estado do agent
        self.is_active = True
        self.is_busy = False
        self.capabilities = self._define_capabilities()
        
        # Cliente LLM unificado
        self._llm_client = None
        self._setup_llm(llm_provider, llm_model, llm_api_key, use_mock_llm)
        
        self.logger.info(f"Agent '{name}' initialized")
    
    def _setup_llm(
        self,
        provider: Optional[str],
        model: Optional[str],
        api_key: Optional[str],
        use_mock: bool
    ):
        """Configurar cliente LLM unificado."""
        try:
            from tools.integrations.llm_client import create_llm_client
            
            self._llm_client = create_llm_client(
                provider=provider,
                model=model,
                api_key=api_key,
                use_mock=use_mock
            )
            
            if self._llm_client.is_available():
                provider_name = getattr(self._llm_client, 'provider', 'unknown')
                model_name = getattr(self._llm_client, 'model', 'unknown')
                self.logger.info(f"LLM client configured: {provider_name}/{model_name}")
                if "llm_processing" not in self.capabilities:
                    self.capabilities.append("llm_processing")
            else:
                self.logger.warning("LLM client not available, using basic processing")
                
        except Exception as e:
            self.logger.warning(f"Failed to setup LLM client: {e}")
            self._llm_client = None
    
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger do agent."""
        logger = logging.getLogger(f"agent.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - AGENT[{self.name}] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _define_capabilities(self) -> List[str]:
        """
        Define as capacidades do agent.
        Deve ser sobrescrito pelos agents especializados.
        
        Returns:
            Lista de capacidades do agent
        """
        return ["basic_communication", "message_handling"]
    
    @abstractmethod
    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma tarefa específica.
        
        Args:
            task: Descrição da tarefa a ser executada
            **kwargs: Argumentos adicionais específicos da tarefa
        
        Returns:
            Resultado da execução da tarefa
        """
        pass
    
    async def send_message(self, recipient: str, content: str, message_type: str = "info") -> bool:
        """
        Envia uma mensagem para outro agent.
        
        Args:
            recipient: Nome do agent destinatário
            content: Conteúdo da mensagem
            message_type: Tipo da mensagem (info, request, response, error)
        
        Returns:
            True se a mensagem foi enviada com sucesso
        """
        try:
            message = AgentMessage(
                sender=self.name,
                recipient=recipient,
                content=content,
                message_type=message_type,
                timestamp=datetime.now()
            )
            
            self.message_history.append(message)
            self.logger.info(f"Message sent to {recipient}: {message_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {recipient}: {e}")
            return False
    
    async def receive_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Recebe e processa uma mensagem de outro agent.
        
        Args:
            message: Mensagem recebida
        
        Returns:
            Resposta à mensagem
        """
        try:
            self.message_history.append(message)
            self.logger.info(f"Message received from {message.sender}: {message.message_type}")
            
            # Processar mensagem baseado no tipo
            if message.message_type == "request":
                return await self._handle_request(message)
            elif message.message_type == "info":
                return await self._handle_info(message)
            else:
                return {
                    "success": True,
                    "message": "Message received and logged"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to process message from {message.sender}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_with_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processar texto usando o cliente LLM configurado.
        
        Args:
            prompt: Prompt para o LLM
            system_message: Mensagem de sistema (contexto)
            temperature: Temperatura para geração
            max_tokens: Máximo de tokens na resposta
            
        Returns:
            Resposta do LLM e metadados
        """
        if not self._llm_client or not self._llm_client.is_available():
            return {
                "success": False,
                "error": "LLM client not available",
                "fallback": True
            }
        
        try:
            from tools.integrations.llm_client import LLMMessage
            
            messages = []
            
            if system_message:
                messages.append(LLMMessage("system", system_message))
            
            messages.append(LLMMessage("user", prompt))
            
            response = await self._llm_client.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            self.logger.info(f"LLM response generated ({response.provider}/{response.model})")
            
            return {
                "success": True,
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage
            }
            
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def has_llm(self) -> bool:
        """Verificar se o agent tem LLM disponível."""
        return self._llm_client is not None and self._llm_client.is_available()
    
    def get_llm_info(self) -> Dict[str, Any]:
        """Obter informações sobre o LLM configurado."""
        if not self.has_llm():
            return {"available": False}
        
        return {
            "available": True,
            "provider": getattr(self._llm_client, 'provider', 'unknown'),
            "model": getattr(self._llm_client, 'model', 'unknown')
        }
    
    async def _handle_request(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Processa uma mensagem de solicitação.
        Pode ser sobrescrito por agents especializados.
        
        Args:
            message: Mensagem de solicitação
        
        Returns:
            Resposta à solicitação
        """
        return {
            "success": True,
            "message": f"Request acknowledged by {self.name}",
            "content": message.content
        }
    
    async def _handle_info(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Processa uma mensagem informativa.
        
        Args:
            message: Mensagem informativa
        
        Returns:
            Confirmação de recebimento
        """
        return {
            "success": True,
            "message": "Information received and processed"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtém o status atual do agent.
        
        Returns:
            Dict com informações de status
        """
        return {
            "name": self.name,
            "is_active": self.is_active,
            "is_busy": self.is_busy,
            "message_count": len(self.message_history),
            "capabilities": self.capabilities,
            "has_llm": self.has_llm(),
            "llm_info": self.get_llm_info(),
            "created_at": self.created_at.isoformat()
        }
    
    def get_capabilities(self) -> List[str]:
        """
        Retorna as capacidades do agent.
        
        Returns:
            Lista de capacidades
        """
        return self.capabilities.copy()
    
    def has_capability(self, capability: str) -> bool:
        """
        Verifica se o agent possui uma capacidade específica.
        
        Args:
            capability: Capacidade a ser verificada
        
        Returns:
            True se o agent possui a capacidade
        """
        return capability in self.capabilities
    
    async def set_busy(self, busy: bool = True):
        """
        Define o estado de ocupado do agent.
        
        Args:
            busy: True se o agent está ocupado
        """
        self.is_busy = busy
        status = "busy" if busy else "available"
        self.logger.info(f"Agent status changed to: {status}")
    
    async def shutdown(self):
        """Desliga o agent graciosamente."""
        self.is_active = False
        self.logger.info(f"Agent '{self.name}' shutting down")
    
    def get_message_history(self, limit: Optional[int] = None) -> List[AgentMessage]:
        """
        Retorna o histórico de mensagens.
        
        Args:
            limit: Número máximo de mensagens a retornar
        
        Returns:
            Lista de mensagens
        """
        if limit:
            return self.message_history[-limit:]
        return self.message_history.copy()
    
    async def clear_history(self):
        """Limpa o histórico de mensagens."""
        self.message_history.clear()
        self.logger.info("Message history cleared")
    
    def __str__(self) -> str:
        """Representação string do agent."""
        return f"Agent(name='{self.name}', active={self.is_active}, capabilities={len(self.capabilities)})"
    
    def __repr__(self) -> str:
        """Representação detalhada do agent."""
        return (
            f"Agent(name='{self.name}', "
            f"active={self.is_active}, "
            f"busy={self.is_busy}, "
            f"capabilities={self.capabilities}, "
            f"has_llm={self.model_client is not None})"
        )


class SimpleAgent(BaseAgent):
    """
    Implementação simples de um agent para testes e exemplos.
    Apenas ecoa as mensagens recebidas.
    """
    
    def __init__(self, name: str, model_client=None, **kwargs):
        super().__init__(name, model_client, **kwargs)
    
    def _define_capabilities(self) -> List[str]:
        return ["basic_communication", "echo", "simple_tasks"]
    
    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma tarefa simples (echo).
        
        Args:
            task: Tarefa a ser executada
            **kwargs: Argumentos adicionais
        
        Returns:
            Resultado da tarefa
        """
        await self.set_busy(True)
        
        try:
            self.logger.info(f"Processing task: {task}")
            
            # Simular algum processamento
            await asyncio.sleep(0.1)
            
            result = {
                "success": True,
                "agent": self.name,
                "task": task,
                "response": f"Task '{task}' processed by {self.name}",
                "timestamp": datetime.now().isoformat()
            }
            
            if self.model_client:
                # Se tem LLM, usar para processar a tarefa
                try:
                    llm_response = await self.model_client.invoke(
                        f"Process this task: {task}. Respond briefly and helpfully."
                    )
                    result["llm_response"] = llm_response
                except Exception as e:
                    self.logger.warning(f"LLM processing failed: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "task": task
            }
        finally:
            await self.set_busy(False)


# Exemplo de uso
async def test_base_agent():
    """Testa a funcionalidade básica do BaseAgent."""
    
    print("=== Teste do BaseAgent ===")
    
    # Criar agent simples
    agent1 = SimpleAgent("test_agent_1")
    agent2 = SimpleAgent("test_agent_2")
    
    # Testar status
    print(f"Agent 1 Status: {agent1.get_status()}")
    print(f"Agent 1 Capabilities: {agent1.get_capabilities()}")
    
    # Testar execução de tarefa
    result = await agent1.run("Test task execution")
    print(f"Task Result: {result}")
    
    # Testar comunicação entre agents
    await agent1.send_message("test_agent_2", "Hello from agent 1", "info")
    
    message = AgentMessage(
        sender="test_agent_2",
        recipient="test_agent_1",
        content="Hello back from agent 2",
        message_type="info",
        timestamp=datetime.now()
    )
    
    response = await agent1.receive_message(message)
    print(f"Message Response: {response}")
    
    # Verificar histórico
    history = agent1.get_message_history()
    print(f"Message History: {len(history)} messages")
    
    # Desligar agents
    await agent1.shutdown()
    await agent2.shutdown()


if __name__ == "__main__":
    asyncio.run(test_base_agent())
