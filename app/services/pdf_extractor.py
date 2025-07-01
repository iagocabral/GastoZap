import PyPDF2
import re
from typing import Dict, List, Any, Optional
import logging
from app.models.invoice import Fatura, Transacao
from app.utils.pdf_utils import PDFValidator

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Classe responsável por extrair dados de faturas de cartão de crédito em PDF.
    """
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrai dados de uma fatura de cartão de crédito em PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Um dicionário com os dados extraídos
        """
        try:
            logger.info(f"Iniciando extração do arquivo: {pdf_path}")
            
            # Valida se é um PDF válido
            if not PDFValidator.validate_pdf(pdf_path):
                raise ValueError(f"Arquivo PDF inválido: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Instancia o modelo da fatura
                fatura = Fatura()
                
                # Processa cada página do PDF
                full_text = ""
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    full_text += text
                    
                # Extrai informações básicas usando expressões regulares
                # Nota: Essas expressões precisarão ser adaptadas com base no formato real da fatura
                fatura.titular = self._extract_pattern(full_text, r"Nome:\s*([^\n]*)")
                fatura.numero_cartao = self._extract_pattern(full_text, r"Cartão:\s*([•\*\d]+)")
                fatura.data_fechamento = self._extract_pattern(full_text, r"Fechamento:\s*(\d{2}/\d{2}/\d{4})")
                fatura.valor_total = self._extract_pattern(full_text, r"Total:\s*R\$\s*([\d\.,]+)")
                
                # Extrai transações
                transacoes = self._extract_transactions(full_text)
                for transacao in transacoes:
                    fatura.adicionar_transacao(transacao)
                
                # Calcula o valor total se não foi encontrado na fatura
                if not fatura.valor_total:
                    total = fatura.calcular_total()
                    fatura.valor_total = f"{total:.2f}"
                
                logger.info("Extração concluída com sucesso")
                return fatura.to_dict()
                
        except Exception as e:
            logger.error(f"Erro ao extrair dados do PDF: {str(e)}")
            raise
    
    def _extract_pattern(self, text: str, pattern: str) -> Optional[str]:
        """
        Extrai informações usando expressões regulares.
        
        Args:
            text: Texto a ser processado
            pattern: Padrão de expressão regular
            
        Returns:
            String extraída ou None se não encontrada
        """
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_transactions(self, text: str) -> List[Transacao]:
        """
        Extrai as transações da fatura.
        Este método precisa ser adaptado com base no formato real das transações na fatura.
        
        Args:
            text: Texto completo da fatura
            
        Returns:
            Lista de objetos Transacao
        """
        transactions = []
        
        # Padrão exemplo para encontrar transações
        # Formato: DD/MM Descrição do estabelecimento 999,99
        transaction_pattern = r"(\d{2}/\d{2})\s+([^\d]+)\s+([\d\.,]+)"
        
        matches = re.finditer(transaction_pattern, text)
        for match in matches:
            if len(match.groups()) >= 3:
                date = match.group(1)
                description = match.group(2).strip()
                value = match.group(3).replace('.', '').replace(',', '.')
                
                # Criamos um objeto Transacao
                transacao = Transacao(
                    data=date,
                    descricao=description,
                    valor=float(value),
                    categoria=self._categorize_transaction(description)
                )
                
                transactions.append(transacao)
        
        return transactions
        
    def _categorize_transaction(self, description: str) -> Optional[str]:
        """
        Categoriza uma transação com base na descrição.
        Esta é uma implementação simples que pode ser melhorada.
        
        Args:
            description: Descrição da transação
            
        Returns:
            Categoria ou None se não for possível categorizar
        """
        description = description.lower()
        
        # Categorias comuns
        if any(word in description for word in ['supermercado', 'mercado', 'hortifruti', 'sacolão']):
            return 'Supermercado'
        elif any(word in description for word in ['restaurante', 'lanchonete', 'bar', 'pizza', 'ifood', 'rappi']):
            return 'Alimentação'
        elif any(word in description for word in ['farmacia', 'drogaria', 'remedio', 'hospital', 'clinica', 'medico']):
            return 'Saúde'
        elif any(word in description for word in ['uber', 'taxi', '99', 'transporte', 'onibus', 'metro', 'trem']):
            return 'Transporte'
        elif any(word in description for word in ['cinema', 'teatro', 'show', 'ingresso', 'netflix', 'spotify']):
            return 'Entretenimento'
        
        return None
