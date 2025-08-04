#!/usr/bin/env python3
"""
Utilitário para validar e testar configuração do ADK.
"""

import sys
import os
import asyncio

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.utils.env_config import print_config_status, validate_llm_setup, get_llm_config


async def test_llm_connection():
    """Testa conexão com o LLM configurado."""
    print("\n🧪 Testando Conexão LLM...")
    print("-" * 30)
    
    try:
        from tools.integrations.llm_client import create_llm_client, LLMMessage
        
        config = get_llm_config()
        client = create_llm_client(
            provider=config["provider"] if not config["use_mock"] else None,
            model=config["model"],
            api_key=config["api_key"],
            use_mock=config["use_mock"]
        )
        
        if not client.is_available():
            print("❌ Cliente LLM não está disponível")
            return False
        
        # Teste simples
        messages = [
            LLMMessage("system", "Você é um assistente de teste."),
            LLMMessage("user", "Responda apenas 'OK' se você conseguir me entender.")
        ]
        
        print(f"📡 Enviando mensagem de teste para {config['provider']}...")
        response = await client.generate(messages, temperature=0.1)
        
        print(f"✅ Resposta recebida: {response.content[:50]}...")
        if response.usage:
            print(f"📊 Tokens: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


async def test_calendar_connection():
    """Testa conexão com o Google Calendar."""
    print("\n📅 Testando Conexão Google Calendar...")
    print("-" * 40)
    
    try:
        from tools.integrations.google_calendar_client import create_calendar_client
        from tools.utils.env_config import get_calendar_config
        
        config = get_calendar_config()
        
        if config["use_mock"]:
            print("🎭 Usando cliente mock - teste não necessário")
            return True
        
        client = create_calendar_client()
        
        print("📡 Testando listagem de calendários...")
        calendars = await client.list_calendars()
        
        if calendars:
            print(f"✅ Encontrados {len(calendars)} calendários:")
            for cal in calendars[:3]:  # Mostrar apenas os primeiros 3
                print(f"   📅 {cal.get('summary', 'Sem nome')} ({cal.get('id', 'sem-id')[:20]}...)")
        else:
            print("⚠️ Nenhum calendário encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


def check_env_file():
    """Verifica se o arquivo .env existe e tem as configurações básicas."""
    print("\n📋 Verificando Arquivo .env...")
    print("-" * 30)
    
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado")
        print("💡 Dicas:")
        print("   1. cp .env.example .env")
        print("   2. Edite .env com suas configurações")
        print("   3. Consulte API_KEYS_GUIDE.md")
        return False
    
    print("✅ Arquivo .env encontrado")
    
    # Verificar variáveis importantes
    important_vars = [
        ("OPENAI_API_KEY", "Chave do OpenAI"),
        ("GOOGLE_API_KEY", "Chave do Google Gemini"),
        ("GROQ_API_KEY", "Chave do Groq"),
        ("ADK_LLM_PROVIDER", "Provedor LLM preferido")
    ]
    
    configured = 0
    for var, desc in important_vars:
        value = os.getenv(var)
        if value and value != f"{var.lower().replace('_', '-')}-here":
            print(f"   ✅ {desc}: configurado")
            configured += 1
        else:
            print(f"   ⚪ {desc}: não configurado")
    
    if configured == 0:
        print("⚠️ Nenhuma chave de API configurada - usando apenas mock")
    else:
        print(f"✅ {configured} configurações encontradas")
    
    return True


async def run_full_test():
    """Executa todos os testes."""
    print("🔧 ADK Configuration Validator")
    print("=" * 50)
    
    # 1. Verificar arquivo .env
    env_ok = check_env_file()
    
    # 2. Mostrar status da configuração
    print_config_status()
    
    # 3. Validar configuração LLM
    llm_validation = validate_llm_setup()
    
    # 4. Testar conexão LLM
    llm_ok = await test_llm_connection()
    
    # 5. Testar Google Calendar
    calendar_ok = await test_calendar_connection()
    
    # Resumo final
    print("\n📊 Resumo dos Testes")
    print("=" * 30)
    print(f"📋 Arquivo .env: {'✅' if env_ok else '❌'}")
    print(f"🧠 Configuração LLM: {'✅' if llm_validation['valid'] else '❌'}")
    print(f"🔌 Conexão LLM: {'✅' if llm_ok else '❌'}")
    print(f"📅 Google Calendar: {'✅' if calendar_ok else '❌'}")
    
    all_ok = env_ok and llm_validation['valid'] and llm_ok and calendar_ok
    
    if all_ok:
        print("\n🎉 Todas as configurações estão funcionando!")
        print("🚀 Execute: ./run_example.sh")
    else:
        print("\n⚠️ Algumas configurações precisam de atenção")
        print("📖 Consulte API_KEYS_GUIDE.md para ajuda")
    
    return all_ok


if __name__ == "__main__":
    try:
        result = asyncio.run(run_full_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Teste cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        sys.exit(1)
