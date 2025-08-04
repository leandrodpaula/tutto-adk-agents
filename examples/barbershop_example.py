"""
Exemplo de uso do Barbershop Scheduler Agent

Este exemplo demonstra como usar o agent para gerenciar agendamentos
de barbearia no Google Calendar.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o agent (ajustar path se necessário)
from agents.specialized.barbershop_scheduler_agent import BarbershopSchedulerAgent
from tools.integrations.google_calendar_client import create_calendar_client


async def setup_example():
    """Configura o ambiente de exemplo."""
    
    print("=== Configuração do Barbershop Scheduler Agent ===\n")
    
    # Carregar configurações de ambiente
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from tools.utils.env_config import get_llm_config, get_calendar_config, validate_llm_setup
        
        # Obter configurações
        llm_config = get_llm_config()
        calendar_config = get_calendar_config()
        llm_validation = validate_llm_setup()
        
        # Mostrar status da configuração
        print(f"🧠 LLM Configurado: {llm_config['provider'].upper()}")
        if llm_config['model']:
            print(f"   Modelo: {llm_config['model']}")
        
        if llm_validation['valid']:
            print(f"   Status: ✅ Configuração válida")
        else:
            print(f"   Status: ⚠️ Usando fallback")
            for error in llm_validation['errors']:
                print(f"   ❌ {error}")
        
        print(f"\n📅 Google Calendar: {'🎭 Mock' if calendar_config['use_mock'] else '✅ Real'}")
        if not calendar_config['use_mock']:
            print(f"   Calendário: {calendar_config['calendar_id']}")
        
    except ImportError:
        # Fallback se não conseguir importar configurações
        llm_config = {
            "provider": os.getenv("ADK_LLM_PROVIDER", "mock"),
            "model": os.getenv("ADK_LLM_MODEL"),
            "api_key": None,
            "use_mock": True
        }
        calendar_config = {"use_mock": True}
        print("⚠️ Usando configuração manual (env_config não disponível)")
    
    # Detectar provedor LLM das variáveis de ambiente ou parâmetro
    env_provider = os.getenv("ADK_LLM_PROVIDER")
    if env_provider:
        llm_config["provider"] = env_provider
        print(f"🔄 Provedor alterado via env: {env_provider.upper()}")
    
    # Criar agent com configurações carregadas
    calendar_id = calendar_config.get("calendar_id", "primary")
    if not isinstance(calendar_id, str):
        calendar_id = "primary"
    
    agent = BarbershopSchedulerAgent(
        name="barbearia_exemplo",
        calendar_id=calendar_id,
        llm_provider=llm_config["provider"] if not llm_config["use_mock"] else None,
        llm_model=llm_config.get("model"),
        llm_api_key=llm_config.get("api_key"),
        use_mock_llm=llm_config["use_mock"]
    )
    
    # Configurar cliente calendar mock se necessário
    if calendar_config["use_mock"]:
        from tools.integrations.google_calendar_client import MockGoogleCalendarClient
        agent.calendar_client = MockGoogleCalendarClient()  # type: ignore
        print("   (Para usar Google Calendar real, configure as credenciais no .env)")
    
    return agent


async def exemplo_1_criar_agendamento(agent):
    """Exemplo 1: Criar um novo agendamento."""
    
    print("\n" + "="*50)
    print("📅 EXEMPLO 1: Criar Agendamento")
    print("="*50)
    
    # Texto natural em português
    solicitacao = "Quero agendar um corte completo para João Silva amanhã às 15:00, telefone 11999999999"
    
    print(f"📝 Solicitação: {solicitacao}")
    print("\n⏳ Processando...")
    
    resultado = await agent.create_appointment(solicitacao)
    
    print(f"\n✅ Resultado:")
    if resultado["success"]:
        print(f"   ✓ Agendamento criado com sucesso!")
        print(f"   📋 ID: {resultado.get('appointment_id', 'N/A')}")
        print(f"   👤 Cliente: {resultado['details']['customer']}")
        print(f"   ✂️ Serviço: {resultado['details']['service']}")
        print(f"   📅 Data: {resultado['details']['date']}")
        print(f"   🕐 Horário: {resultado['details']['time']}")
        print(f"   ⏱️ Duração: {resultado['details']['duration']}")
    else:
        print(f"   ❌ Erro: {resultado.get('message', 'Erro desconhecido')}")


async def exemplo_2_consultar_disponibilidade(agent):
    """Exemplo 2: Consultar disponibilidade."""
    
    print("\n" + "="*50)
    print("🔍 EXEMPLO 2: Consultar Disponibilidade")
    print("="*50)
    
    # Consultar disponibilidade para amanhã
    amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"📅 Consultando disponibilidade para: {amanha}")
    print("\n⏳ Processando...")
    
    resultado = await agent.check_availability(date=amanha)
    
    print(f"\n📊 Resultado:")
    if resultado["success"]:
        print(f"   📅 Data: {resultado['date']}")
        print(f"   🏪 Horário comercial: {resultado['business_hours']}")
        print(f"   ✅ Disponível: {'Sim' if resultado['available'] else 'Não'}")
        
        if resultado["available"]:
            print(f"   🕐 Horários livres: {resultado['total_slots']} slots")
            for i, slot in enumerate(resultado['available_slots'][:5], 1):
                print(f"      {i}. {slot}")
            if len(resultado['available_slots']) > 5:
                print(f"      ... e mais {len(resultado['available_slots']) - 5} horários")
        else:
            print(f"   ℹ️ Motivo: {resultado.get('reason', 'Não informado')}")
    else:
        print(f"   ❌ Erro: {resultado.get('message', 'Erro desconhecido')}")


async def exemplo_3_listar_agendamentos(agent):
    """Exemplo 3: Listar agendamentos."""
    
    print("\n" + "="*50)
    print("📋 EXEMPLO 3: Listar Agendamentos")
    print("="*50)
    
    print("📅 Listando agendamentos dos próximos 7 dias...")
    print("\n⏳ Processando...")
    
    resultado = await agent.list_appointments()
    
    print(f"\n📊 Resultado:")
    if resultado["success"]:
        print(f"   📅 Período: {resultado['period']}")
        print(f"   📋 Total de agendamentos: {resultado['total']}")
        
        if resultado['total'] > 0:
            print(f"\n   📝 Agendamentos:")
            for i, appointment in enumerate(resultado['appointments'], 1):
                print(f"      {i}. {appointment['title']}")
                print(f"         🕐 {appointment['start']} - {appointment['end']}")
                print(f"         📋 Status: {appointment['status']}")
                if appointment.get('description'):
                    print(f"         📝 Detalhes: {appointment['description'][:100]}...")
                print()
        else:
            print(f"   ℹ️ Nenhum agendamento encontrado para o período")
    else:
        print(f"   ❌ Erro: {resultado.get('message', 'Erro desconhecido')}")


async def exemplo_4_horarios_disponiveis_servico(agent):
    """Exemplo 4: Consultar horários para serviço específico."""
    
    print("\n" + "="*50)
    print("✂️ EXEMPLO 4: Horários para Serviço Específico")
    print("="*50)
    
    servico = "corte_completo"
    amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"✂️ Serviço: {servico}")
    print(f"📅 Data: {amanha}")
    print("\n⏳ Processando...")
    
    resultado = await agent.get_available_slots(date=amanha, service=servico)
    
    print(f"\n📊 Resultado:")
    if resultado["success"]:
        print(f"   📅 Data: {resultado['date']}")
        print(f"   ✂️ Serviço: {resultado['service']}")
        print(f"   🕐 Horários disponíveis: {resultado['total_slots']}")
        
        if resultado['total_slots'] > 0:
            print(f"\n   📝 Slots disponíveis:")
            for i, slot in enumerate(resultado['available_slots'], 1):
                print(f"      {i}. {slot['time']} - {slot['end_time']} ({slot['duration']} min)")
        else:
            print(f"   ℹ️ Nenhum horário disponível para este serviço")
    else:
        print(f"   ❌ Erro: {resultado.get('message', 'Erro desconhecido')}")


async def exemplo_5_comandos_naturais(agent):
    """Exemplo 5: Comandos em linguagem natural."""
    
    print("\n" + "="*50)
    print("💬 EXEMPLO 5: Comandos em Linguagem Natural")
    print("="*50)
    
    comandos = [
        "Verificar se segunda-feira de manhã está livre",
        "Agendar corte para Maria Santos na terça às 14:30",
        "Listar os agendamentos de hoje",
        "Cancelar agendamento do João",
        "Que horários estão livres sexta-feira?"
    ]
    
    for i, comando in enumerate(comandos, 1):
        print(f"\n{i}. 💬 Comando: \"{comando}\"")
        print("   ⏳ Processando...")
        
        try:
            resultado = await agent.run(comando)
            
            if resultado["success"]:
                print(f"   ✅ Resposta: {resultado.get('message', 'Comando processado')}")
                if 'details' in resultado:
                    for key, value in resultado['details'].items():
                        print(f"      📋 {key}: {value}")
            else:
                print(f"   ❌ Erro: {resultado.get('message', 'Erro desconhecido')}")
                
        except Exception as e:
            print(f"   ❌ Erro interno: {str(e)}")
        
        # Pequena pausa entre comandos
        await asyncio.sleep(0.5)


async def main():
    """Função principal do exemplo."""
    
    try:
        # Configurar agent
        agent = await setup_example()
        
        print(f"\n🤖 Agent '{agent.name}' configurado com sucesso!")
        print(f"📋 Capacidades: {', '.join(agent.get_capabilities())}")
        print(f"🏪 Horários de funcionamento:")
        for dia, horario in agent.business_hours.items():
            if horario["start"] != "closed":
                print(f"   📅 {dia.capitalize()}: {horario['start']} - {horario['end']}")
            else:
                print(f"   📅 {dia.capitalize()}: Fechado")
        
        print(f"\n✂️ Serviços disponíveis:")
        for servico, detalhes in agent.services.items():
            print(f"   🔸 {servico}: {detalhes['duration']}min - R$ {detalhes['price']:.2f}")
        
        # Executar exemplos
        await exemplo_1_criar_agendamento(agent)
        await exemplo_2_consultar_disponibilidade(agent)
        await exemplo_3_listar_agendamentos(agent)
        await exemplo_4_horarios_disponiveis_servico(agent)
        await exemplo_5_comandos_naturais(agent)
        
        print("\n" + "="*50)
        print("🎉 Todos os exemplos executados com sucesso!")
        print("="*50)
        
        # Mostrar estatísticas do agent
        status = agent.get_status()
        print(f"\n📊 Status final do agent:")
        print(f"   🤖 Nome: {status['name']}")
        print(f"   ✅ Ativo: {status['is_active']}")
        print(f"   ⏱️ Ocupado: {status['is_busy']}")
        print(f"   💬 Mensagens processadas: {status['message_count']}")
        print(f"   🧠 LLM disponível: {status['has_llm']}")
        
        print(f"\n💡 Dicas para uso em produção:")
        print(f"   1. Configure as credenciais do Google Calendar")
        print(f"   2. Adicione um modelo LLM para melhor compreensão de linguagem natural")
        print(f"   3. Personalize os horários de funcionamento e serviços")
        print(f"   4. Implemente notificações por WhatsApp/SMS")
        print(f"   5. Adicione validações de negócio específicas")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Iniciando exemplo do Barbershop Scheduler Agent...")
    asyncio.run(main())
