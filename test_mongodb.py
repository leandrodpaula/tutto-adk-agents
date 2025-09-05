#!/usr/bin/env python3
"""
Teste simples para verificar se a conexão com MongoDB está funcionando.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from tutto.tools.utils.database import MongoDatabase
    from tutto.config.settings import Settings
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def test_mongodb_connection():
        """Testa a conexão com MongoDB."""
        try:
            logger.info("Testando conexão com MongoDB...")
            
            # Teste básico de conexão
            test_data = {"test": "data", "timestamp": "2025-09-05"}
            
            # Teste insert
            result = MongoDatabase.insert_one("test_collection", test_data)
            logger.info(f"✅ Insert realizado com sucesso: {result.acknowledged}")
            
            # Teste find
            found_data = MongoDatabase.find("test_collection", {"test": "data"})
            logger.info(f"✅ Find realizado com sucesso. Encontrados {len(found_data)} registros")
            
            # Teste delete (limpeza)
            delete_result = MongoDatabase.delete_many("test_collection", {"test": "data"})
            logger.info(f"✅ Delete realizado com sucesso. Removidos {delete_result.deleted_count} registros")
            
            logger.info("🎉 Todos os testes passaram! MongoDB está funcionando corretamente!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão com MongoDB: {e}")
            logger.info("Verifique se o MongoDB está rodando e as credenciais estão corretas no .env")
            return False

    if __name__ == "__main__":
        logger.info("Iniciando testes MongoDB...")
        logger.info(f"MongoDB URI configurado: {Settings.MONGODB_URI}")
        
        if test_mongodb_connection():
            sys.exit(0)
        else:
            sys.exit(1)

except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que as dependências estão instaladas: uv sync")
    sys.exit(1)
