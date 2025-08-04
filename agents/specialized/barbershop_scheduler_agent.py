"""
Barbershop Scheduler Agent

Agent especializado para gerenciar agendamentos de barbearia no Google Calendar.
Permite criar, consultar, modificar e cancelar agendamentos.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from agents.core.base_agent import BaseAgent
from tools.integrations.google_calendar_client import GoogleCalendarClient
from tools.custom.time_parser import TimeParser


@dataclass
class AppointmentRequest:
    """Estrutura de dados para solicitação de agendamento."""
    customer_name: str
    customer_phone: str
    service_type: str
    preferred_date: str
    preferred_time: str
    duration_minutes: int = 60
    notes: Optional[str] = None


@dataclass
class Appointment:
    """Estrutura de dados para agendamento."""
    id: str
    customer_name: str
    customer_phone: str
    service_type: str
    start_time: datetime
    end_time: datetime
    status: str
    notes: Optional[str] = None


class BarbershopSchedulerAgent(BaseAgent):
    """
    Agent para gerenciamento de agendamentos de barbearia.
    
    Funcionalidades:
    - Criar novos agendamentos
    - Consultar disponibilidade
    - Listar agendamentos
    - Modificar agendamentos existentes
    - Cancelar agendamentos
    - Enviar lembretes
    """
    
    def __init__(
        self,
        name: str = "barbershop_scheduler",
        calendar_id: str = "primary",
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        use_mock_llm: bool = False,
        **kwargs
    ):
        """
        Inicializar o agent de agendamento de barbearia.
        
        Args:
            name: Nome do agent
            calendar_id: ID do calendário do Google Calendar
            llm_provider: Provedor de LLM (openai, gemini, groq)
            llm_model: Modelo específico do LLM
            llm_api_key: Chave da API do LLM
            use_mock_llm: Usar cliente LLM mock
            **kwargs: Argumentos adicionais
        """
        # Inicializar agent base com suporte a LLM
        super().__init__(
            name=name,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            use_mock_llm=use_mock_llm,
            **kwargs
        )
        
        # Configurações específicas da barbearia
        self.calendar_id = calendar_id
        self.business_hours = {
            "monday": {"start": "09:00", "end": "18:00"},
            "tuesday": {"start": "09:00", "end": "18:00"},
            "wednesday": {"start": "09:00", "end": "18:00"},
            "thursday": {"start": "09:00", "end": "18:00"},
            "friday": {"start": "09:00", "end": "19:00"},
            "saturday": {"start": "08:00", "end": "17:00"},
            "sunday": {"start": "closed", "end": "closed"}
        }
        
        # Serviços disponíveis com duração e preço
        self.services = {
            "corte_simples": {"duration": 30, "price": 25.00},
            "corte_barba": {"duration": 45, "price": 35.00},
            "corte_completo": {"duration": 60, "price": 45.00},
            "barba": {"duration": 30, "price": 20.00},
            "sobrancelha": {"duration": 15, "price": 15.00}
        }
        
        # Cliente do Google Calendar
        try:
            from tools.integrations.google_calendar_client import GoogleCalendarClient
            self.calendar_client = GoogleCalendarClient()
        except Exception as e:
            self.logger.error(f"Erro ao inicializar cliente Google Calendar: {e}")
            # Usar cliente mock como fallback
            from tools.integrations.google_calendar_client import MockGoogleCalendarClient
            self.calendar_client = MockGoogleCalendarClient()  # type: ignore
        
        # Parser de tempo em português
        from tools.custom.time_parser import TimeParser
        self.time_parser = TimeParser()
        
        # Configurações da barbearia
        self.business_hours = {
            "monday": {"start": "09:00", "end": "18:00"},
            "tuesday": {"start": "09:00", "end": "18:00"},
            "wednesday": {"start": "09:00", "end": "18:00"},
            "thursday": {"start": "09:00", "end": "18:00"},
            "friday": {"start": "09:00", "end": "19:00"},
            "saturday": {"start": "08:00", "end": "17:00"},
            "sunday": {"start": "closed", "end": "closed"}
        }
        
        self.services = {
            "corte_simples": {"duration": 30, "price": 25.00},
            "corte_barba": {"duration": 45, "price": 35.00},
            "corte_completo": {"duration": 60, "price": 45.00},
            "barba": {"duration": 30, "price": 20.00},
            "sobrancelha": {"duration": 15, "price": 15.00}
        }
    
    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma tarefa relacionada ao agendamento.
        
        Args:
            task: Descrição da tarefa ou comando
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resultado da operação
        """
        try:
            # Usar LLM para entender a intenção se disponível
            if self.has_llm():
                intent = await self._analyze_intent(task)
                return await self._execute_intent(intent, task, **kwargs)
            else:
                # Fallback para análise simples por palavras-chave
                return await self._simple_task_handler(task, **kwargs)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao processar solicitação de agendamento"
            }
    
    async def _analyze_intent(self, task: str) -> Dict[str, Any]:
        """Analisa a intenção do usuário usando LLM."""
        system_message = """Você é um assistente especializado em agendamentos de barbearia.
        Analise a solicitação e identifique a intenção do cliente."""
        
        prompt = f"""
        Solicitação: "{task}"
        
        Identifique a intenção principal dentre:
        - agendar: criar novo agendamento
        - consultar: verificar agendamento específico
        - modificar: alterar agendamento existente
        - cancelar: cancelar agendamento
        - listar: listar agendamentos
        - disponibilidade: verificar horários livres

        Responda em JSON com:
        {{
            "intent": "intenção_identificada",
            "confidence": 0.95,
            "extracted_info": {{
                "customer_name": "nome_se_mencionado",
                "date": "data_se_mencionada", 
                "time": "horario_se_mencionado",
                "service": "servico_se_mencionado"
            }}
        }}
        """
        
        llm_response = await self.process_with_llm(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3
        )
        
        if llm_response["success"]:
            try:
                import json
                return json.loads(llm_response["content"])
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Erro ao parsear resposta LLM: {e}, usando fallback")
        
        # Fallback: classificação simples baseada em palavras-chave
        return self._simple_intent_classification(task)
    
    def _simple_intent_classification(self, task: str) -> Dict[str, Any]:
        """Classificação simples de intenção baseada em palavras-chave."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["agendar", "marcar", "quero"]):
            intent = "agendar"
        elif any(word in task_lower for word in ["listar", "mostrar", "ver agendamentos"]):
            intent = "listar"
        elif any(word in task_lower for word in ["cancelar", "desmarcar"]):
            intent = "cancelar"
        elif any(word in task_lower for word in ["modificar", "alterar", "mudar"]):
            intent = "modificar"
        elif any(word in task_lower for word in ["disponibilidade", "horários livres", "disponível"]):
            intent = "disponibilidade"
        else:
            intent = "agendar"  # padrão
        
        return {
            "intent": intent,
            "confidence": 0.8,
            "extracted_info": {}
        }
    
    async def _execute_intent(self, intent_data: Dict, task: str, **kwargs) -> Dict[str, Any]:
        """Executa a ação baseada na intenção identificada."""
        intent = intent_data.get("intent", "agendar")
        extracted_info = intent_data.get("extracted_info", {})
        
        if intent == "agendar":
            return await self.create_appointment(task, **kwargs)
        elif intent == "consultar":
            return await self.check_availability(**kwargs)
        elif intent == "listar":
            return await self.list_appointments(**kwargs)
        elif intent == "modificar":
            return await self._modify_appointment_placeholder(**kwargs)
        elif intent == "cancelar":
            return await self.cancel_appointment(**kwargs)
        elif intent == "disponibilidade":
            return await self.get_available_slots(**kwargs)
        else:
            return await self.create_appointment(task, **kwargs)
    
    async def _modify_appointment_placeholder(self, **kwargs) -> Dict[str, Any]:
        """Placeholder para modificação de agendamentos."""
        return {
            "success": False,
            "message": "Funcionalidade de modificação ainda não implementada",
            "suggestion": "Use cancel_appointment para cancelar e create_appointment para criar novo"
        }

    async def _simple_task_handler(self, task: str, **kwargs) -> Dict[str, Any]:
        """Handler simples para quando LLM não está disponível."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["agendar", "marcar", "quero"]):
            return await self.create_appointment(task, **kwargs)
        elif any(word in task_lower for word in ["listar", "mostrar"]):
            return await self.list_appointments(**kwargs)
        elif any(word in task_lower for word in ["cancelar", "desmarcar"]):
            return await self.cancel_appointment(**kwargs)
        elif any(word in task_lower for word in ["disponibilidade", "horários"]):
            return await self.check_availability(**kwargs)
        else:
            return await self.create_appointment(task, **kwargs)
    
    async def create_appointment(self, request: str, **kwargs) -> Dict[str, Any]:
        """
        Cria um novo agendamento.
        
        Args:
            request: Descrição do agendamento ou objeto AppointmentRequest
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resultado da criação do agendamento
        """
        try:
            # Extrair informações do agendamento
            if isinstance(request, str):
                appointment_data = await self._extract_appointment_info(request)
            else:
                appointment_data = request
            
            # Validar dados
            validation_result = await self._validate_appointment(appointment_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": validation_result["message"]
                }
            
            # Verificar disponibilidade
            availability = await self._check_slot_availability(
                appointment_data["date"], 
                appointment_data["time"],
                appointment_data.get("duration", 60)
            )
            
            if not availability["available"]:
                return {
                    "success": False,
                    "message": f"Horário não disponível. Sugestões: {availability['suggestions']}"
                }
            
            # Criar evento no Google Calendar
            event_data = {
                "summary": f"Barbearia - {appointment_data['customer_name']}",
                "description": f"""
                Cliente: {appointment_data['customer_name']}
                Telefone: {appointment_data.get('phone', 'Não informado')}
                Serviço: {appointment_data['service']}
                Observações: {appointment_data.get('notes', 'Nenhuma')}
                """,
                "start": {
                    "dateTime": appointment_data["start_datetime"].isoformat(),
                    "timeZone": "America/Sao_Paulo"
                },
                "end": {
                    "dateTime": appointment_data["end_datetime"].isoformat(),
                    "timeZone": "America/Sao_Paulo"
                },
                "attendees": [
                    {"email": appointment_data.get("customer_email", "")}
                ] if appointment_data.get("customer_email") else [],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 60},
                        {"method": "popup", "minutes": 15}
                    ]
                }
            }
            
            event_result = await self.calendar_client.create_event(
                self.calendar_id, 
                event_data
            )
            
            if event_result["success"]:
                return {
                    "success": True,
                    "appointment_id": event_result["event_id"],
                    "message": f"Agendamento criado com sucesso para {appointment_data['customer_name']}",
                    "details": {
                        "customer": appointment_data["customer_name"],
                        "service": appointment_data["service"],
                        "date": appointment_data["date"],
                        "time": appointment_data["time"],
                        "duration": f"{appointment_data.get('duration', 60)} minutos"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro ao criar agendamento: {event_result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao criar agendamento"
            }
    
    async def _extract_appointment_info(self, request: str) -> Dict[str, Any]:
        """Extrai informações de agendamento da string de solicitação."""
        if self.has_llm():
            system_message = """Você é um assistente especializado em extrair informações de agendamentos de barbearia."""
            
            prompt = f"""
            Extraia as informações de agendamento da seguinte solicitação:
            
            "{request}"
            
            Serviços disponíveis: {list(self.services.keys())}
            
            Responda em JSON:
            {{
                "customer_name": "nome do cliente",
                "phone": "telefone se mencionado",
                "service": "tipo de serviço",
                "date": "data no formato YYYY-MM-DD",
                "time": "horário no formato HH:MM",
                "notes": "observações adicionais"
            }}
            """
            
            llm_response = await self.process_with_llm(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3
            )
            
            if llm_response["success"]:
                import json
                try:
                    extracted = json.loads(llm_response["content"])
                    # Adicionar duração baseada no serviço
                    service_key = extracted.get("service", "corte_simples")
                    extracted["duration"] = self.services.get(service_key, {}).get("duration", 60)
                    return extracted
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.warning(f"Erro ao parsear extração LLM: {e}")
        
        # Fallback: extração simples
        return {
            "customer_name": "Cliente",
            "service": "corte_simples",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "duration": 60
        }
    
    async def _validate_appointment(self, appointment_data: Dict) -> Dict[str, Any]:
        """Valida os dados do agendamento."""
        required_fields = ["customer_name", "service", "date", "time"]
        
        for field in required_fields:
            if not appointment_data.get(field):
                return {
                    "valid": False,
                    "message": f"Campo obrigatório não informado: {field}"
                }
        
        # Validar serviço
        if appointment_data["service"] not in self.services:
            return {
                "valid": False,
                "message": f"Serviço inválido. Disponíveis: {list(self.services.keys())}"
            }
        
        # Validar data (não pode ser no passado)
        try:
            appointment_date = datetime.strptime(appointment_data["date"], "%Y-%m-%d").date()
            if appointment_date < datetime.now().date():
                return {
                    "valid": False,
                    "message": "Data não pode ser no passado"
                }
        except ValueError:
            return {
                "valid": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD"
            }
        
        # Validar horário de funcionamento
        day_of_week = appointment_date.strftime("%A").lower()
        business_hours = self.business_hours.get(day_of_week, {})
        
        if business_hours.get("start") == "closed":
            return {
                "valid": False,
                "message": "Barbearia fechada neste dia"
            }
        
        # Criar datetime objects
        appointment_datetime = datetime.strptime(
            f"{appointment_data['date']} {appointment_data['time']}", 
            "%Y-%m-%d %H:%M"
        )
        
        duration = appointment_data.get("duration", 60)
        end_datetime = appointment_datetime + timedelta(minutes=duration)
        
        appointment_data["start_datetime"] = appointment_datetime
        appointment_data["end_datetime"] = end_datetime
        
        return {"valid": True, "message": "Dados válidos"}
    
    async def _check_slot_availability(self, date: str, time: str, duration: int) -> Dict[str, Any]:
        """Verifica se o horário está disponível."""
        start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Buscar eventos existentes no período
        existing_events = await self.calendar_client.get_events(
            self.calendar_id,
            start_datetime,
            end_datetime
        )
        
        if existing_events["success"] and existing_events["events"]:
            # Gerar sugestões de horários alternativos
            suggestions = await self._generate_alternative_slots(date, duration)
            return {
                "available": False,
                "reason": "Horário já ocupado",
                "suggestions": suggestions
            }
        
        return {"available": True}
    
    async def _generate_alternative_slots(self, date: str, duration: int) -> List[str]:
        """Gera sugestões de horários alternativos."""
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = appointment_date.strftime("%A").lower()
        business_hours = self.business_hours.get(day_of_week, {})
        
        if business_hours.get("start") == "closed":
            return []
        
        suggestions = []
        start_hour = int(business_hours["start"].split(":")[0])
        end_hour = int(business_hours["end"].split(":")[0])
        
        # Gerar slots de 30 em 30 minutos
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                slot_datetime = datetime.strptime(f"{date} {slot_time}", "%Y-%m-%d %H:%M")
                slot_end = slot_datetime + timedelta(minutes=duration)
                
                # Verificar se o slot cabe no horário de funcionamento
                if slot_end.hour < end_hour or (slot_end.hour == end_hour and slot_end.minute == 0):
                    # Verificar disponibilidade (simplified)
                    suggestions.append(slot_time)
                
                if len(suggestions) >= 3:
                    break
            if len(suggestions) >= 3:
                break
        
        return suggestions
    
    async def check_availability(self, date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Consulta disponibilidade para uma data específica."""
        if not date:
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            appointment_date = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = appointment_date.strftime("%A").lower()
            business_hours = self.business_hours.get(day_of_week, {})
            
            if business_hours.get("start") == "closed":
                return {
                    "success": True,
                    "date": date,
                    "available": False,
                    "reason": "Barbearia fechada neste dia"
                }
            
            # Buscar eventos existentes
            start_of_day = appointment_date.replace(hour=0, minute=0, second=0)
            end_of_day = appointment_date.replace(hour=23, minute=59, second=59)
            
            existing_events = await self.calendar_client.get_events(
                self.calendar_id,
                start_of_day,
                end_of_day
            )
            
            available_slots = await self._generate_available_slots(date, existing_events.get("events", []))
            
            return {
                "success": True,
                "date": date,
                "available": len(available_slots) > 0,
                "business_hours": f"{business_hours['start']} - {business_hours['end']}",
                "available_slots": available_slots,
                "total_slots": len(available_slots)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao consultar disponibilidade"
            }
    
    async def _generate_available_slots(self, date: str, existing_events: List) -> List[str]:
        """Gera lista de horários disponíveis."""
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = appointment_date.strftime("%A").lower()
        business_hours = self.business_hours.get(day_of_week, {})
        
        if business_hours.get("start") == "closed":
            return []
        
        # Converter eventos existentes para períodos ocupados
        occupied_periods = []
        for event in existing_events:
            start_time = event.get("start", {}).get("dateTime", "")
            end_time = event.get("end", {}).get("dateTime", "")
            if start_time and end_time:
                occupied_periods.append((start_time, end_time))
        
        # Gerar slots disponíveis
        available_slots = []
        start_hour = int(business_hours["start"].split(":")[0])
        end_hour = int(business_hours["end"].split(":")[0])
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                slot_datetime = datetime.strptime(f"{date} {slot_time}", "%Y-%m-%d %H:%M")
                
                # Verificar se o slot não conflita com eventos existentes
                is_available = True
                for start_str, end_str in occupied_periods:
                    event_start = datetime.fromisoformat(start_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    event_end = datetime.fromisoformat(end_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    
                    if event_start <= slot_datetime < event_end:
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(slot_time)
        
        return available_slots
    
    async def list_appointments(self, date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Lista agendamentos para uma data específica ou período."""
        try:
            if date:
                start_date = datetime.strptime(date, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1)
            else:
                # Próximos 7 dias por padrão
                start_date = datetime.now()
                end_date = start_date + timedelta(days=7)
            
            events_result = await self.calendar_client.get_events(
                self.calendar_id,
                start_date,
                end_date
            )
            
            if not events_result["success"]:
                return {
                    "success": False,
                    "message": f"Erro ao buscar agendamentos: {events_result['error']}"
                }
            
            appointments = []
            for event in events_result.get("events", []):
                appointment = {
                    "id": event.get("id"),
                    "title": event.get("summary", ""),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "description": event.get("description", ""),
                    "status": event.get("status", "")
                }
                appointments.append(appointment)
            
            return {
                "success": True,
                "appointments": appointments,
                "total": len(appointments),
                "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao listar agendamentos"
            }
    
    async def cancel_appointment(self, appointment_id: str, **kwargs) -> Dict[str, Any]:
        """Cancela um agendamento."""
        try:
            result = await self.calendar_client.delete_event(self.calendar_id, appointment_id)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Agendamento cancelado com sucesso",
                    "appointment_id": appointment_id
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro ao cancelar agendamento: {result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao cancelar agendamento"
            }
    
    async def get_available_slots(self, date: Optional[str] = None, service: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Retorna slots disponíveis para um serviço específico."""
        if not date:
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        duration = 60  # padrão
        if service and service in self.services:
            duration = self.services[service]["duration"]
        
        availability = await self.check_availability(date)
        
        if availability["success"] and availability["available"]:
            # Filtrar slots baseado na duração do serviço
            suitable_slots = []
            available_slots = availability["available_slots"]
            
            for slot in available_slots:
                slot_datetime = datetime.strptime(f"{date} {slot}", "%Y-%m-%d %H:%M")
                slot_end = slot_datetime + timedelta(minutes=duration)
                
                # Verificar se o slot + duração ainda está dentro do horário comercial
                day_of_week = slot_datetime.strftime("%A").lower()
                business_hours = self.business_hours.get(day_of_week, {})
                end_hour = int(business_hours["end"].split(":")[0])
                
                if slot_end.hour < end_hour or (slot_end.hour == end_hour and slot_end.minute == 0):
                    suitable_slots.append({
                        "time": slot,
                        "duration": duration,
                        "service": service or "qualquer",
                        "end_time": slot_end.strftime("%H:%M")
                    })
            
            return {
                "success": True,
                "date": date,
                "service": service or "qualquer",
                "available_slots": suitable_slots,
                "total_slots": len(suitable_slots)
            }
        else:
            return availability


# Exemplo de uso
async def main():
    """Exemplo de uso do BarbershopSchedulerAgent."""
    
    # Inicializar agent
    agent = BarbershopSchedulerAgent("barbershop_scheduler")
    
    # Teste 1: Criar agendamento
    print("=== Teste 1: Criar Agendamento ===")
    result = await agent.create_appointment(
        "Agendar corte para João Silva amanhã às 14:00, telefone 11999999999"
    )
    print(f"Resultado: {result}")
    
    # Teste 2: Consultar disponibilidade
    print("\n=== Teste 2: Consultar Disponibilidade ===")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    availability = await agent.check_availability(date=tomorrow)
    print(f"Disponibilidade: {availability}")
    
    # Teste 3: Listar agendamentos
    print("\n=== Teste 3: Listar Agendamentos ===")
    appointments = await agent.list_appointments()
    print(f"Agendamentos: {appointments}")


if __name__ == "__main__":
    asyncio.run(main())
