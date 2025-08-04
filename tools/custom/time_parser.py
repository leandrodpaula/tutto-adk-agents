"""
Time Parser

Utilitário para parsing e manipulação de datas e horários.
Suporte para diferentes formatos de entrada em português.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import calendar


class TimeParser:
    """
    Parser para datas e horários em português brasileiro.
    
    Suporte para formatos como:
    - "amanhã às 14:00"
    - "segunda-feira 15:30"
    - "12/03/2024 10:00"
    - "hoje de manhã"
    """
    
    def __init__(self):
        self.weekdays_pt = {
            'segunda': 0, 'segunda-feira': 0,
            'terça': 1, 'terca': 1, 'terça-feira': 1, 'terca-feira': 1,
            'quarta': 2, 'quarta-feira': 2,
            'quinta': 3, 'quinta-feira': 3,
            'sexta': 4, 'sexta-feira': 4,
            'sábado': 5, 'sabado': 5,
            'domingo': 6
        }
        
        self.months_pt = {
            'janeiro': 1, 'jan': 1,
            'fevereiro': 2, 'fev': 2,
            'março': 3, 'mar': 3, 'marco': 3,
            'abril': 4, 'abr': 4,
            'maio': 5, 'mai': 5,
            'junho': 6, 'jun': 6,
            'julho': 7, 'jul': 7,
            'agosto': 8, 'ago': 8,
            'setembro': 9, 'set': 9,
            'outubro': 10, 'out': 10,
            'novembro': 11, 'nov': 11,
            'dezembro': 12, 'dez': 12
        }
        
        self.time_periods = {
            'manhã': (9, 0),
            'manha': (9, 0),
            'tarde': (14, 0),
            'noite': (19, 0),
            'meio-dia': (12, 0),
            'meio dia': (12, 0),
            'meio-dia': (12, 0),
        }
        
        # Padrões regex para diferentes formatos
        self.patterns = {
            'time_24h': r'(\d{1,2}):(\d{2})',
            'time_12h': r'(\d{1,2}):(\d{2})\s*(am|pm|h)',
            'date_br': r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
            'date_iso': r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
            'relative_day': r'(hoje|amanhã|amanha|depois de amanhã)',
            'weekday': r'(segunda|terça|terca|quarta|quinta|sexta|sábado|sabado|domingo)[\-\s]?feira?',
            'period': r'(manhã|manha|tarde|noite|meio[\-\s]?dia)',
        }
    
    def parse_datetime(self, text: str, base_date: datetime = None) -> Optional[datetime]:
        """
        Extrai data e hora de um texto em português.
        
        Args:
            text: Texto contendo informações de data/hora
            base_date: Data base para cálculos relativos
        
        Returns:
            Objeto datetime ou None se não conseguir parsear
        """
        if base_date is None:
            base_date = datetime.now()
        
        text = text.lower().strip()
        
        # Tentar diferentes estratégias de parsing
        result = (
            self._parse_explicit_datetime(text, base_date) or
            self._parse_relative_datetime(text, base_date) or
            self._parse_weekday_time(text, base_date) or
            self._parse_date_only(text, base_date) or
            self._parse_time_only(text, base_date)
        )
        
        return result
    
    def _parse_explicit_datetime(self, text: str, base_date: datetime) -> Optional[datetime]:
        """Parse formato explícito: '12/03/2024 14:30'"""
        # Buscar data no formato brasileiro
        date_match = re.search(self.patterns['date_br'], text)
        if not date_match:
            # Tentar formato ISO
            date_match = re.search(self.patterns['date_iso'], text)
            if date_match:
                year, month, day = map(int, date_match.groups())
            else:
                return None
        else:
            day, month, year = map(int, date_match.groups())
        
        # Buscar horário
        time_match = re.search(self.patterns['time_24h'], text)
        if time_match:
            hour, minute = map(int, time_match.groups())
        else:
            hour, minute = 9, 0  # Padrão manhã
        
        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None
    
    def _parse_relative_datetime(self, text: str, base_date: datetime) -> Optional[datetime]:
        """Parse datas relativas: 'hoje', 'amanhã', etc."""
        relative_match = re.search(self.patterns['relative_day'], text)
        if not relative_match:
            return None
        
        relative_day = relative_match.group(1)
        
        if relative_day == 'hoje':
            target_date = base_date.date()
        elif relative_day in ['amanhã', 'amanha']:
            target_date = (base_date + timedelta(days=1)).date()
        elif relative_day == 'depois de amanhã':
            target_date = (base_date + timedelta(days=2)).date()
        else:
            return None
        
        # Buscar horário
        time_part = self._extract_time(text)
        if time_part:
            hour, minute = time_part
        else:
            hour, minute = 9, 0  # Padrão manhã
        
        return datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def _parse_weekday_time(self, text: str, base_date: datetime) -> Optional[datetime]:
        """Parse dia da semana: 'segunda-feira 15:30'"""
        weekday_match = re.search(self.patterns['weekday'], text)
        if not weekday_match:
            return None
        
        weekday_name = weekday_match.group(1)
        if weekday_name.endswith('feira'):
            weekday_name = weekday_name[:-5]  # Remove 'feira'
        
        weekday_name = weekday_name.strip('-').strip()
        
        if weekday_name not in self.weekdays_pt:
            return None
        
        target_weekday = self.weekdays_pt[weekday_name]
        current_weekday = base_date.weekday()
        
        # Calcular dias até o próximo dia da semana
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Se for hoje ou passou, vai para a próxima semana
            days_ahead += 7
        
        target_date = (base_date + timedelta(days=days_ahead)).date()
        
        # Buscar horário
        time_part = self._extract_time(text)
        if time_part:
            hour, minute = time_part
        else:
            hour, minute = 9, 0  # Padrão manhã
        
        return datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def _parse_date_only(self, text: str, base_date: datetime) -> Optional[datetime]:
        """Parse apenas data: '12/03' (assume ano atual)"""
        # Formato dd/mm
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})(?![/\-]\d{4})', text)
        if match:
            day, month = map(int, match.groups())
            year = base_date.year
            
            # Se a data já passou este ano, assume próximo ano
            try:
                target_date = datetime(year, month, day)
                if target_date.date() <= base_date.date():
                    target_date = datetime(year + 1, month, day)
                
                # Usar horário padrão ou extrair do texto
                time_part = self._extract_time(text)
                if time_part:
                    hour, minute = time_part
                else:
                    hour, minute = 9, 0
                
                return target_date.replace(hour=hour, minute=minute)
            except ValueError:
                return None
        
        return None
    
    def _parse_time_only(self, text: str, base_date: datetime) -> Optional[datetime]:
        """Parse apenas horário (assume hoje): '14:30'"""
        time_part = self._extract_time(text)
        if time_part:
            hour, minute = time_part
            target_date = base_date.date()
            
            # Se o horário já passou hoje, assume amanhã
            target_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            if target_datetime <= base_date:
                target_datetime += timedelta(days=1)
            
            return target_datetime
        
        return None
    
    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        """Extrai horário do texto."""
        # Tentar formato 24h
        time_match = re.search(self.patterns['time_24h'], text)
        if time_match:
            hour, minute = map(int, time_match.groups())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # Tentar formato 12h
        time_match = re.search(self.patterns['time_12h'], text)
        if time_match:
            hour, minute, period = time_match.groups()
            hour, minute = int(hour), int(minute)
            
            if period.lower() == 'pm' and hour != 12:
                hour += 12
            elif period.lower() == 'am' and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # Tentar períodos do dia
        for period, (default_hour, default_minute) in self.time_periods.items():
            if period in text:
                return (default_hour, default_minute)
        
        return None
    
    def parse_date_range(self, text: str, base_date: datetime = None) -> Optional[Tuple[datetime, datetime]]:
        """
        Parse um intervalo de datas.
        
        Args:
            text: Texto contendo intervalo (ex: "de segunda a sexta")
            base_date: Data base para cálculos
        
        Returns:
            Tupla (data_inicio, data_fim) ou None
        """
        if base_date is None:
            base_date = datetime.now()
        
        text = text.lower()
        
        # Padrão "de X a Y"
        range_patterns = [
            r'de\s+(.+?)\s+a\s+(.+)',
            r'desde\s+(.+?)\s+até\s+(.+)',
            r'entre\s+(.+?)\s+e\s+(.+)'
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, text)
            if match:
                start_text, end_text = match.groups()
                
                start_date = self.parse_datetime(start_text, base_date)
                end_date = self.parse_datetime(end_text, base_date)
                
                if start_date and end_date:
                    return (start_date, end_date)
        
        return None
    
    def format_datetime_pt(self, dt: datetime) -> str:
        """
        Formata datetime em português brasileiro.
        
        Args:
            dt: Objeto datetime
        
        Returns:
            String formatada em português
        """
        weekdays_pt_names = [
            'Segunda-feira', 'Terça-feira', 'Quarta-feira', 
            'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'
        ]
        
        months_pt_names = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        weekday_name = weekdays_pt_names[dt.weekday()]
        month_name = months_pt_names[dt.month]
        
        return f"{weekday_name}, {dt.day} de {month_name} de {dt.year} às {dt.hour:02d}:{dt.minute:02d}"
    
    def is_business_day(self, dt: datetime, business_days: List[int] = None) -> bool:
        """
        Verifica se é um dia útil.
        
        Args:
            dt: Data para verificar
            business_days: Lista de dias da semana (0=segunda, 6=domingo)
        
        Returns:
            True se for dia útil
        """
        if business_days is None:
            business_days = [0, 1, 2, 3, 4, 5]  # Segunda a sábado
        
        return dt.weekday() in business_days
    
    def get_next_business_day(self, dt: datetime, business_days: List[int] = None) -> datetime:
        """
        Retorna o próximo dia útil.
        
        Args:
            dt: Data base
            business_days: Lista de dias úteis
        
        Returns:
            Próximo dia útil
        """
        if business_days is None:
            business_days = [0, 1, 2, 3, 4, 5]  # Segunda a sábado
        
        next_day = dt + timedelta(days=1)
        while next_day.weekday() not in business_days:
            next_day += timedelta(days=1)
        
        return next_day
    
    def validate_time_format(self, time_str: str) -> bool:
        """
        Valida se a string está em formato de horário válido.
        
        Args:
            time_str: String de horário
        
        Returns:
            True se válido
        """
        time_part = self._extract_time(time_str)
        return time_part is not None


# Exemplo de uso e testes
def test_time_parser():
    """Testa o TimeParser com diferentes formatos."""
    parser = TimeParser()
    base_date = datetime(2024, 8, 4, 10, 0)  # Domingo, 4 de agosto de 2024, 10:00
    
    test_cases = [
        "amanhã às 14:00",
        "segunda-feira 15:30",
        "hoje de tarde",
        "12/03/2024 10:00",
        "sexta 16:00",
        "15:30",
        "quarta-feira de manhã"
    ]
    
    print("=== Teste do TimeParser ===")
    for test_case in test_cases:
        result = parser.parse_datetime(test_case, base_date)
        if result:
            formatted = parser.format_datetime_pt(result)
            print(f"'{test_case}' -> {formatted}")
        else:
            print(f"'{test_case}' -> Não foi possível parsear")


if __name__ == "__main__":
    test_time_parser()
