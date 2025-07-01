import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class PDFValidator:
    """Utilitário para validar arquivos PDF"""
    
    @staticmethod
    def validate_pdf(file_path: str) -> bool:
        """
        Verifica se o arquivo é um PDF válido
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            True se for um PDF válido, False caso contrário
        """
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return False
            
        # Verifica a extensão do arquivo
        if not file_path.lower().endswith('.pdf'):
            logger.error(f"Arquivo não é um PDF: {file_path}")
            return False
            
        # Verifica o tamanho do arquivo (limite de 10MB)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # em MB
        if file_size > 10:
            logger.error(f"Arquivo muito grande ({file_size:.2f}MB): {file_path}")
            return False
            
        # Verifica o magic number (assinatura) do PDF
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    logger.error(f"Assinatura de PDF inválida: {file_path}")
                    return False
        except Exception as e:
            logger.error(f"Erro ao verificar assinatura de PDF: {str(e)}")
            return False
            
        return True


def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    Remove arquivos temporários
    
    Args:
        file_paths: Lista de caminhos para arquivos a serem removidos
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Arquivo temporário removido: {path}")
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário {path}: {str(e)}")


def format_currency(value: float) -> str:
    """
    Formata um valor para o formato de moeda brasileira
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        String formatada (ex: R$ 1.234,56)
    """
    if value is None:
        return "R$ 0,00"
        
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
