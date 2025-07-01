import os
import logging
from typing import Dict, Any

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
EXPORTS_DIR = os.path.join(STATIC_DIR, "exports")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Configurações da API
API_CONFIG: Dict[str, Any] = {
    "title": "Assistente Financeiro",
    "description": "API para extrair dados de faturas de cartão de crédito em PDF",
    "version": "0.1.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
}

# Garantir que os diretórios necessários existam
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
