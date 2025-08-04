"""
Google Calendar Client

Cliente para integração com Google Calendar API.
Permite criar, buscar, modificar e deletar eventos.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleCalendarClient:
    """
    Cliente para integração com Google Calendar API.
    
    Suporte para autenticação via:
    - Service Account (recomendado para produção)
    - OAuth2 (para desenvolvimento)
    """
    
    def __init__(self, credentials_path: str = None, calendar_id: str = "primary"):
        self.calendar_id = calendar_id
        self.service = None
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google Calendar dependencies not installed. "
                "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
            )
    
    async def initialize(self) -> Dict[str, Any]:
        """Inicializa a conexão com Google Calendar API."""
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Usar Service Account
                credentials = ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            else:
                # Para desenvolvimento, usar credenciais do ambiente
                credentials_info = {
                    "type": "service_account",
                    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
                    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                }
                
                credentials = ServiceAccountCredentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            
            return {"success": True, "message": "Google Calendar client initialized"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo evento no calendário.
        
        Args:
            calendar_id: ID do calendário
            event_data: Dados do evento
        
        Returns:
            Resultado da operação
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return {
                "success": True,
                "event_id": event.get('id'),
                "event_link": event.get('htmlLink'),
                "message": "Evento criado com sucesso"
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao criar evento no Google Calendar"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao criar evento"
            }
    
    async def get_events(self, calendar_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Busca eventos em um período específico.
        
        Args:
            calendar_id: ID do calendário
            start_time: Data/hora de início
            end_time: Data/hora de fim
        
        Returns:
            Lista de eventos encontrados
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                "success": True,
                "events": events,
                "total": len(events)
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao buscar eventos no Google Calendar"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao buscar eventos"
            }
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um evento existente.
        
        Args:
            calendar_id: ID do calendário
            event_id: ID do evento
            event_data: Novos dados do evento
        
        Returns:
            Resultado da operação
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            return {
                "success": True,
                "event_id": updated_event.get('id'),
                "message": "Evento atualizado com sucesso"
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao atualizar evento no Google Calendar"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao atualizar evento"
            }
    
    async def delete_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """
        Deleta um evento.
        
        Args:
            calendar_id: ID do calendário
            event_id: ID do evento
        
        Returns:
            Resultado da operação
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "message": "Evento deletado com sucesso"
            }
            
        except HttpError as e:
            if e.resp.status == 410:
                return {
                    "success": True,
                    "message": "Evento já foi deletado"
                }
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao deletar evento no Google Calendar"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao deletar evento"
            }
    
    async def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """
        Busca um evento específico por ID.
        
        Args:
            calendar_id: ID do calendário
            event_id: ID do evento
        
        Returns:
            Dados do evento
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "event": event
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao buscar evento no Google Calendar"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao buscar evento"
            }
    
    async def list_calendars(self) -> Dict[str, Any]:
        """
        Lista todos os calendários disponíveis.
        
        Returns:
            Lista de calendários
        """
        try:
            if not self.service:
                init_result = await self.initialize()
                if not init_result["success"]:
                    return init_result
            
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            return {
                "success": True,
                "calendars": calendars,
                "total": len(calendars)
            }
            
        except HttpError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.resp.status}: {e.content.decode()}",
                "message": "Erro ao listar calendários"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao listar calendários"
            }


# Classe Mock para desenvolvimento/testes sem Google API
class MockGoogleCalendarClient:
    """Cliente mock para desenvolvimento sem Google API."""
    
    def __init__(self, calendar_id: str = "primary"):
        self.calendar_id = calendar_id
        self.events = {}  # Simulação de armazenamento de eventos
        self.event_counter = 1
    
    async def initialize(self) -> Dict[str, Any]:
        return {"success": True, "message": "Mock Calendar client initialized"}
    
    async def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = f"mock_event_{self.event_counter}"
        self.event_counter += 1
        
        self.events[event_id] = {
            "id": event_id,
            "summary": event_data.get("summary", ""),
            "description": event_data.get("description", ""),
            "start": event_data.get("start", {}),
            "end": event_data.get("end", {}),
            "status": "confirmed"
        }
        
        return {
            "success": True,
            "event_id": event_id,
            "event_link": f"https://calendar.google.com/event?eid={event_id}",
            "message": "Evento criado com sucesso (MOCK)"
        }
    
    async def get_events(self, calendar_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        # Retorna eventos mock que se encaixam no período
        filtered_events = []
        for event in self.events.values():
            # Simulação simples - retorna todos os eventos
            filtered_events.append(event)
        
        return {
            "success": True,
            "events": filtered_events,
            "total": len(filtered_events)
        }
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        if event_id in self.events:
            self.events[event_id].update(event_data)
            return {
                "success": True,
                "event_id": event_id,
                "message": "Evento atualizado com sucesso (MOCK)"
            }
        else:
            return {
                "success": False,
                "error": "Evento não encontrado",
                "message": "Evento não existe"
            }
    
    async def delete_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        if event_id in self.events:
            del self.events[event_id]
            return {
                "success": True,
                "message": "Evento deletado com sucesso (MOCK)"
            }
        else:
            return {
                "success": True,
                "message": "Evento já foi deletado (MOCK)"
            }
    
    async def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        if event_id in self.events:
            return {
                "success": True,
                "event": self.events[event_id]
            }
        else:
            return {
                "success": False,
                "error": "Evento não encontrado",
                "message": "Evento não existe"
            }
    
    async def list_calendars(self) -> Dict[str, Any]:
        mock_calendars = [
            {
                "id": "primary",
                "summary": "Calendário Principal",
                "description": "Calendário principal da barbearia"
            }
        ]
        
        return {
            "success": True,
            "calendars": mock_calendars,
            "total": len(mock_calendars)
        }


# Factory function para escolher o cliente apropriado
def create_calendar_client(use_mock: bool = False, **kwargs) -> Any:
    """
    Cria um cliente do Google Calendar.
    
    Args:
        use_mock: Se True, usa cliente mock para desenvolvimento
        **kwargs: Argumentos para o cliente
    
    Returns:
        Cliente do Google Calendar (real ou mock)
    """
    if use_mock or not GOOGLE_AVAILABLE:
        return MockGoogleCalendarClient(**kwargs)
    else:
        return GoogleCalendarClient(**kwargs)
