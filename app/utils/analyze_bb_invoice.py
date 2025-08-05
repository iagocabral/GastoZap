"""
Utilitário para analisar e mostrar o conteúdo de uma fatura do Banco do Brasil
para identificação dos padrões necessários para a extração de dados.
"""
import os
import sys
import PyPDF2
import re

def analyze_pdf(pdf_path: str) -> None:
    """
    Analisa um arquivo PDF e exibe seu conteúdo textual para análise de padrões.
    
    Args:
        pdf_path: Caminho para o arquivo PDF da fatura do Banco do Brasil
    """
    if not os.path.exists(pdf_path):
        print(f"Arquivo não encontrado: {pdf_path}")
        return
        
    try:
        # Abre o arquivo PDF
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Número de páginas
            num_pages = len(reader.pages)
            print(f"O PDF tem {num_pages} página(s)")
            
            # Extrai e mostra o texto de cada página
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                print(f"\n{'=' * 50}")
                print(f"CONTEÚDO DA PÁGINA {page_num + 1}")
                print(f"{'=' * 50}\n")
                print(text)
                
                # Tenta identificar alguns padrões comuns
                print(f"\n{'=' * 50}")
                print("IDENTIFICAÇÃO DE PADRÕES")
                print(f"{'=' * 50}")
                
                # Tenta identificar o titular
                titular_patterns = [
                    r"Nome:?\s*([^\n]+)",
                    r"Cliente:?\s*([^\n]+)",
                    r"Titular:?\s*([^\n]+)"
                ]
                
                for pattern in titular_patterns:
                    match = re.search(pattern, text)
                    if match:
                        print(f"Possível titular: {match.group(1).strip()}")
                
                # Tenta identificar o número do cartão
                cartao_patterns = [
                    r"Cartão:?\s*([\d\s\*•]+)",
                    r"Cartão final:?\s*([\d\s\*•]+)",
                    r"Conta Cartão:?\s*([\d\s\*•]+)"
                ]
                
                for pattern in cartao_patterns:
                    match = re.search(pattern, text)
                    if match:
                        print(f"Possível número do cartão: {match.group(1).strip()}")
                
                # Tenta identificar datas importantes
                data_patterns = [
                    r"Vencimento:?\s*(\d{2}/\d{2}/\d{4})",
                    r"Data de vencimento:?\s*(\d{2}/\d{2}/\d{4})",
                    r"Fechamento:?\s*(\d{2}/\d{2}/\d{4})"
                ]
                
                for pattern in data_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        print(f"Possível data importante: {match.group(0)}")
                
                # Tenta identificar valores totais
                valor_patterns = [
                    r"Total:?\s*R\$\s*([\d\.,]+)",
                    r"Valor total:?\s*R\$\s*([\d\.,]+)",
                    r"Total da fatura:?\s*R\$\s*([\d\.,]+)"
                ]
                
                for pattern in valor_patterns:
                    match = re.search(pattern, text)
                    if match:
                        print(f"Possível valor total: R$ {match.group(1).strip()}")
                
                # Tenta identificar transações
                # Este padrão é uma estimativa inicial e precisará ser refinado
                transacao_pattern = r"(\d{2}/\d{2})\s+([^\d]+?)\s+(R?\$?\s*[\d\.,]+)"
                transacoes = re.finditer(transacao_pattern, text)
                
                print("\nPossíveis transações encontradas:")
                for idx, match in enumerate(transacoes, 1):
                    if len(match.groups()) >= 3:
                        data = match.group(1)
                        descricao = match.group(2).strip()
                        valor = match.group(3)
                        print(f"{idx}. Data: {data}, Descrição: {descricao}, Valor: {valor}")
    
    except Exception as e:
        print(f"Erro ao analisar o PDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_bb_invoice.py <caminho_do_pdf>")
    else:
        pdf_path = sys.argv[1]
        analyze_pdf(pdf_path)
