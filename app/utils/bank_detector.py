"""
Utilitário para detectar qual o banco emissor de uma fatura de cartão de crédito.
"""
import os
import PyPDF2
import re
from typing import Optional, Dict, Any

class BankDetector:
    """
    Classe responsável por detectar o banco emissor de uma fatura de cartão de crédito.
    """
    
    # Padrões para identificação de diferentes bancos
    BANK_PATTERNS = {
        'banco_do_brasil': [
            r'OUROCARD',
            r'BB\s+',
            r'Banco\s+do\s+Brasil',
            r'www\.bb\.com\.br',
            r'Iago\s+De\s+Paula\s+Cabra',
            r'Cartão\s+\d+',
            r'SALDO\s+FATURA\s+ANTERIOR',
            r'Pagamentos/Créditos'
        ],
        'nubank': [
            r'Nu\s+Pagamentos',
            r'Nubank',
            r'www\.nubank\.com\.br'
        ],
        'itau': [
            r'Ita[úu]',
            r'www\.itau\.com\.br'
        ],
        'bradesco': [
            r'Bradesco',
            r'www\.bradesco\.com\.br'
        ],
        'santander': [
            r'Santander',
            r'www\.santander\.com\.br'
        ]
        # Adicione mais bancos conforme necessário
    }
    
    @classmethod
    def detect_bank(cls, pdf_path: str) -> Optional[str]:
        """
        Detecta o banco emissor de uma fatura de cartão de crédito.
        
        Args:
            pdf_path: Caminho para o arquivo PDF da fatura
            
        Returns:
            String com o identificador do banco ou None se não for possível identificar
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        try:
            # Extrai o texto do PDF
            text = cls._extract_text_from_pdf(pdf_path)
            
            # Verifica os padrões de cada banco
            for bank_id, patterns in cls.BANK_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        return bank_id
            
            # Se não encontrou nenhum padrão conhecido
            return None
                
        except Exception as e:
            print(f"Erro ao detectar banco do PDF: {str(e)}")
            return None
    
    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extrai o texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        full_text = ""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extrai o texto das primeiras páginas (geralmente suficiente para identificar o banco)
            pages_to_check = min(2, len(reader.pages))
            for page_num in range(pages_to_check):
                page = reader.pages[page_num]
                full_text += page.extract_text()
                
        return full_text
    
    @classmethod
    def get_available_banks(cls) -> Dict[str, str]:
        """
        Retorna um dicionário com os bancos disponíveis para identificação.
        
        Returns:
            Dicionário com id do banco e nome amigável
        """
        return {
            'banco_do_brasil': 'Banco do Brasil',
            'nubank': 'Nubank',
            'itau': 'Itaú',
            'bradesco': 'Bradesco',
            'santander': 'Santander',
            # Adicione mais bancos conforme necessário
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python bank_detector.py <caminho_do_pdf>")
    else:
        pdf_path = sys.argv[1]
        bank = BankDetector.detect_bank(pdf_path)
        
        if bank:
            banks = BankDetector.get_available_banks()
            print(f"Banco detectado: {banks.get(bank, bank)}")
        else:
            print("Não foi possível identificar o banco emissor da fatura.")
