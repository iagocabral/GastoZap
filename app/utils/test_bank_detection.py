"""
Utilitário para testar a detecção automática de bancos em faturas de cartão de crédito.
"""
import os
import sys
import json
from bank_detector import BankDetector
from ..services.pdf_extractor import PDFExtractor

def test_bank_detection(pdf_path: str) -> None:
    """
    Testa a detecção automática de banco para uma fatura.
    
    Args:
        pdf_path: Caminho para o arquivo PDF da fatura
    """
    if not os.path.exists(pdf_path):
        print(f"Arquivo não encontrado: {pdf_path}")
        return
        
    try:
        # Detecta o banco
        print(f"\n{'=' * 50}")
        print("DETECÇÃO DE BANCO")
        print(f"{'=' * 50}")
        
        bank_id = BankDetector.detect_bank(pdf_path)
        banks = BankDetector.get_available_banks()
        
        if bank_id:
            bank_name = banks.get(bank_id, bank_id)
            print(f"Banco detectado: {bank_name} (ID: {bank_id})")
            
            # Mostra os padrões usados para este banco
            extractor = PDFExtractor()
            patterns = extractor.BANK_EXTRACTORS.get(bank_id, {})
            
            print(f"\n{'=' * 50}")
            print("PADRÕES DE EXTRAÇÃO")
            print(f"{'=' * 50}")
            
            for field, pattern in patterns.items():
                print(f"- {field}: {pattern}")
                
            # Extrai os dados
            print(f"\n{'=' * 50}")
            print("DADOS EXTRAÍDOS")
            print(f"{'=' * 50}")
            
            extracted_data = extractor.extract(pdf_path, bank_id)
            print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
            
        else:
            print("Não foi possível identificar o banco emissor da fatura.")
            print("Bancos disponíveis:", ", ".join([f"{k} ({v})" for k, v in banks.items()]))
    
    except Exception as e:
        print(f"Erro ao testar detecção de banco: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_bank_detection.py <caminho_do_pdf>")
    else:
        pdf_path = sys.argv[1]
        test_bank_detection(pdf_path)
