"""
Utilitário para carregar configurações de ambiente.
Carrega variáveis do arquivo .env e fornece configurações padrão.
"""

import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """
    Carrega variáveis de ambiente de um arquivo .env.
    
    Args:
        env_path: Caminho para o arquivo .env
        
    Returns:
        Dicionário com as variáveis carregadas
    """
    env_vars = {}
    
    if not os.path.exists(env_path):
        logger.info(f"Arquivo {env_path} não encontrado, usando apenas variáveis do sistema")
        return env_vars
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Pular linhas vazias e comentários
                if not line or line.startswith('#'):
                    continue
                
                # Processar linha no formato KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remover aspas se presentes
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Processar sequências de escape
                    value = value.replace('\\n', '\n').replace('\\t', '\t')
                    
                    env_vars[key] = value
                    
                    # Definir como variável de ambiente se não existir
                    if key not in os.environ:
                        os.environ[key] = value
                else:
                    logger.warning(f"Linha malformada no {env_path}:{line_num}: {line}")
                    
    except Exception as e:
        logger.error(f"Erro ao carregar {env_path}: {e}")
    
    logger.info(f"Carregadas {len(env_vars)} variáveis de {env_path}")
    return env_vars


def load_env():
    """Carrega o arquivo .env (wrapper para load_env_file)."""
    return load_env_file()


def get_llm_config() -> dict:
    """Retorna configuração completa do LLM."""
    load_env()
    
    provider = os.getenv("ADK_LLM_PROVIDER", "openai").lower()
    
    # Mapear provider para API key e modelo padrão
    provider_config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("ADK_OPENAI_MODEL", "gpt-3.5-turbo")
        },
        "gemini": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": os.getenv("ADK_GEMINI_MODEL", "gemini-pro")
        },
        "groq": {
            "api_key": os.getenv("GROQ_API_KEY"),
            "model": os.getenv("ADK_GROQ_MODEL", "llama2-70b-4096")
        }
    }
    
    config = provider_config.get(provider, provider_config["openai"])
    use_mock = not config["api_key"] or config["api_key"].endswith("-here")
    
    return {
        "provider": provider,
        "api_key": config["api_key"],
        "model": config["model"],
        "use_mock": use_mock
    }


def get_calendar_config() -> Dict[str, Any]:
    """
    Obtém configuração do Google Calendar das variáveis de ambiente.
    
    Returns:
        Configuração do Google Calendar
    """
    load_env()
    
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    client_secrets_file = os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
    
    # Verificar se há credenciais configuradas
    has_service_account = (service_account_file and 
                          os.path.exists(service_account_file))
    has_oauth = (client_secrets_file and 
                os.path.exists(client_secrets_file))
    
    # Configuração básica
    config = {
        "service_account_file": service_account_file,
        "client_secrets_file": client_secrets_file,
        "has_service_account": has_service_account,
        "has_oauth": has_oauth,
        "calendar_id": os.getenv("GOOGLE_CALENDAR_ID", "primary"),
        "use_mock": not (has_service_account or has_oauth)
    }
    
    # Se não tiver credenciais, usar mock
    if config["use_mock"]:
        logger.info("Credenciais do Google Calendar não encontradas, usando mock")
    else:
        logger.info("Configuração do Google Calendar carregada")
    
    return config


def get_barbershop_config() -> Dict[str, Any]:
    """
    Obtém configuração da barbearia das variáveis de ambiente.
    
    Returns:
        Configuração da barbearia
    """
    load_env()
    
    config = {
        "name": os.getenv("BARBERSHOP_NAME", "Barbearia ADK"),
        "timezone": os.getenv("BARBERSHOP_TIMEZONE", "America/Sao_Paulo"),
        "phone": os.getenv("BARBERSHOP_PHONE", "+5511999999999"),
        "address": os.getenv("BARBERSHOP_ADDRESS", "Rua das Flores, 123 - São Paulo, SP")
    }
    
    return config


def get_system_config() -> Dict[str, Any]:
    """
    Obtém configuração do sistema das variáveis de ambiente.
    
    Returns:
        Configuração do sistema
    """
    load_env()
    
    config = {
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    return config


def validate_llm_setup() -> Dict[str, Any]:
    """
    Valida se a configuração LLM está correta.
    
    Returns:
        Status da validação
    """
    config = get_llm_config()
    
    validation = {
        "valid": False,
        "provider": config["provider"],
        "has_api_key": bool(config["api_key"]),
        "errors": [],
        "warnings": []
    }
    
    if config["provider"] == "mock":
        validation["valid"] = True
        validation["warnings"].append("Usando cliente LLM mock (sem IA real)")
        return validation
    
    # Validar chave da API
    if not config["api_key"]:
        validation["errors"].append(f"Chave da API não encontrada para {config['provider']}")
        return validation
    
    # Validar formato da chave
    api_key = config["api_key"]
    if config["provider"] == "openai" and not api_key.startswith("sk-"):
        validation["errors"].append("Chave OpenAI deve começar com 'sk-'")
    elif config["provider"] == "gemini" and not api_key.startswith("AIza"):
        validation["errors"].append("Chave Google deve começar com 'AIza'")
    elif config["provider"] == "groq" and not api_key.startswith("gsk_"):
        validation["errors"].append("Chave Groq deve começar com 'gsk_'")
    
    if not validation["errors"]:
        validation["valid"] = True
    
    return validation


def print_config_status():
    """Imprime status da configuração para debug."""
    print("🔧 Status da Configuração ADK")
    print("=" * 50)
    
    # LLM Config
    llm_config = get_llm_config()
    llm_validation = validate_llm_setup()
    
    print(f"🧠 LLM Provider: {llm_config['provider']}")
    print(f"   Modelo: {llm_config['model'] or 'padrão'}")
    print(f"   Chave API: {'✅ Configurada' if llm_config['api_key'] else '❌ Não encontrada'}")
    print(f"   Status: {'✅ Válido' if llm_validation['valid'] else '❌ Inválido'}")
    
    if llm_validation['errors']:
        for error in llm_validation['errors']:
            print(f"   ❌ Erro: {error}")
    
    if llm_validation['warnings']:
        for warning in llm_validation['warnings']:
            print(f"   ⚠️ Aviso: {warning}")
    
    # Calendar Config
    calendar_config = get_calendar_config()
    print(f"\n📅 Google Calendar: {'🎭 Mock' if calendar_config['use_mock'] else '✅ Real'}")
    
    # Barbershop Config
    barbershop_config = get_barbershop_config()
    print(f"\n✂️ Barbearia: {barbershop_config['name']}")
    
    # System Config
    system_config = get_system_config()
    print(f"\n⚙️ Sistema: {system_config['environment']} (log: {system_config['log_level']})")
    
    print("=" * 50)


if __name__ == "__main__":
    print_config_status()
