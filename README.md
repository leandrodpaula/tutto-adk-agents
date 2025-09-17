# Tutto ADK Agents

## Setup

- Python 3.12+
- Crie um virtualenv e instale dependências:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -r requirements.txt

## Teste MongoDB

- Configure o .env com MONGODB_URI
- Execute: python test_mongodb.py

## Observações

- Dependências agora são gerenciadas via requirements.txt.
- Arquivo uv.lock e qualquer configuração do uv podem ser removidos se não forem mais usados.
