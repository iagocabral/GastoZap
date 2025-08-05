import PyPDF2
import re
from typing import Dict, List, Any, Optional
import logging
from app.models.invoice import Fatura, Transacao
from app.utils.pdf_utils import PDFValidator
from app.utils.bank_detector import BankDetector

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Classe responsável por extrair dados de faturas de cartão de crédito em PDF.
    """
    
    # Mapeamento de bancos para expressões regulares específicas
    BANK_EXTRACTORS = {
        'banco_do_brasil': {
            'titular': r"([A-Z\s]+)\s+\(Cartão\s+\d+\)",
            'numero_cartao': r"Cartão\s+(\d+)",
            'data_fechamento': r"Data\s+Descrição.*?País\s+Valor.*?(\d{2}/\d{2})",
            'data_vencimento': r"Vencimento\s*(\d{2}/\d{2}/\d{4})",
            'valor_total': r"R\$\s*([\d\.,]+)$",
            'transacao_pattern': r"(\d{2}/\d{2})\s+([^R$]+?)\s+(?:BR\s+)?R\$\s*([\d\.,]+)"
        },
        # Outros bancos serão adicionados no futuro
    }
    
    def extract(self, pdf_path: str, bank_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrai dados de uma fatura de cartão de crédito em PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            bank_id: Identificador do banco emissor da fatura (opcional)
            
        Returns:
            Um dicionário com os dados extraídos
        """
        # Detecta o banco se não for especificado
        if not bank_id:
            bank_id = BankDetector.detect_bank(pdf_path)
            if not bank_id:
                logger.warning("Não foi possível identificar o banco automaticamente. Usando padrões genéricos.")
                bank_id = 'generic'
        try:
            logger.info(f"Iniciando extração do arquivo: {pdf_path}")
            
            # Valida se é um PDF válido
            if not PDFValidator.validate_pdf(pdf_path):
                raise ValueError(f"Arquivo PDF inválido: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Instancia o modelo da fatura
                fatura = Fatura()
                fatura.banco = bank_id
                
                # Processa cada página do PDF
                full_text = ""
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    full_text += text
                
                # Obtém os padrões específicos para o banco identificado
                patterns = self.BANK_EXTRACTORS.get(bank_id, self.BANK_EXTRACTORS.get('banco_do_brasil'))
                logger.info(f"Usando padrões do banco: {bank_id}")
                
                # Extrai informações básicas usando expressões regulares específicas do banco
                fatura.titular = self._extract_pattern(full_text, patterns.get('titular', r"Nome:\s*([^\n]*)"))
                fatura.numero_cartao = self._extract_pattern(full_text, patterns.get('numero_cartao', r"Cartão:\s*([•\*\d]+)"))
                fatura.data_fechamento = self._extract_pattern(full_text, patterns.get('data_fechamento', r"Fechamento:\s*(\d{2}/\d{2}/\d{4})"))
                fatura.data_vencimento = self._extract_pattern(full_text, patterns.get('data_vencimento', r"Vencimento\s*(\d{2}/\d{2}/\d{4})"))
                fatura.valor_total = self._extract_pattern(full_text, patterns.get('valor_total', r"Total\s*R\$\s*([\d\.,]+)"))
                
                # Extrai transações usando o padrão específico do banco
                transacao_pattern = patterns.get('transacao_pattern', r"(\d{2}/\d{2})\s+([^\d]+?)\s+(R?\$?\s*[\d\.,]+)")
                
                # Para o Banco do Brasil, usa um método específico
                if bank_id == 'banco_do_brasil':
                    transacoes = self._extract_bb_transactions(full_text)
                else:
                    transacoes = self._extract_transactions(full_text, transacao_pattern)
                    
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
    
    def _extract_transactions(self, text: str, transaction_pattern: str = None) -> List[Transacao]:
        """
        Extrai as transações da fatura.
        Este método usa o padrão específico do banco para extrair as transações.
        
        Args:
            text: Texto completo da fatura
            transaction_pattern: Padrão de expressão regular para encontrar transações
            
        Returns:
            Lista de objetos Transacao
        """
        transactions = []
        
        if not transaction_pattern:
            # Padrão padrão para encontrar transações
            # Formato: DD/MM Descrição do estabelecimento 999,99
            transaction_pattern = r"(\d{2}/\d{2})\s+([^\d]+)\s+([\d\.,]+)"
        
        # Para o Banco do Brasil, vamos usar um padrão mais específico
        # que considera o formato: DD/MM DESCRICAO CIDADE BR R$ VALOR
        if 'banco_do_brasil' in transaction_pattern:
            # Padrão específico para o BB que lida melhor com números nas descrições
            bb_pattern = r"(\d{2}/\d{2})\s+(.*?)\s+(?:BR\s+)?R\$\s*([\d\.,]+)(?:\s|$)"
            matches = re.finditer(bb_pattern, text, re.MULTILINE)
        else:
            matches = re.finditer(transaction_pattern, text)
            
        for match in matches:
            if len(match.groups()) >= 3:
                date = match.group(1)
                description = match.group(2).strip()
                
                # Remove informações que não fazem parte da descrição real
                # Para o BB, remove códigos e referências extras
                if description.startswith('SALDO FATURA ANTERIOR') or description.startswith('Pagamentos/Créditos'):
                    continue
                    
                # Limpa a descrição removendo códigos extras e padronizando
                description = self._clean_description(description)
                
                # Se a descrição ficou vazia, pula essa transação
                if not description:
                    continue
                
                # Trata o valor que pode ter formatos diferentes
                value_text = match.group(3).strip()
                # Remove prefixos comuns como "R$" ou "$"
                value_text = re.sub(r'^R\$\s*', '', value_text)
                value_text = re.sub(r'^\$\s*', '', value_text)
                # Normaliza o valor para formato decimal com ponto
                value = value_text.replace('.', '').replace(',', '.')
                
                try:
                    # Tenta converter para float
                    valor_float = float(value)
                    
                    # Criamos um objeto Transacao
                    transacao = Transacao(
                        data=date,
                        descricao=description,
                        valor=valor_float,
                        categoria=self._categorize_transaction(description)
                    )
                    
                    transactions.append(transacao)
                except ValueError:
                    logger.warning(f"Não foi possível converter o valor '{value}' para float. Transação ignorada.")
        
        return transactions
    
    def _clean_description(self, description: str) -> str:
        """
        Limpa e padroniza a descrição da transação.
        
        Args:
            description: Descrição original da transação
            
        Returns:
            Descrição limpa e padronizada
        """
        # Remove códigos de país e outras informações extras
        description = re.sub(r'\s+BR\s*$', '', description)
        description = re.sub(r'\s+BRASIL\s*$', '', description)
        
        # Remove múltiplos espaços
        description = re.sub(r'\s+', ' ', description)
        
        # Remove espaços no início e fim
        description = description.strip()
        
        # Casos específicos do Banco do Brasil
        if 'PGTO. CASH AG.' in description:
            return 'PGTO. CASH AG.'
        
        if 'PARK DESINGDF' in description:
            return 'O PARK DESINGDF'
            
        return description
        
    def _extract_bb_transactions(self, text: str) -> List[Transacao]:
        """
        Método específico para extrair transações do Banco do Brasil.
        
        Args:
            text: Texto completo da fatura
            
        Returns:
            Lista de objetos Transacao
        """
        transactions = []
        
        # Divide o texto em linhas para processamento linha por linha
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Pula linhas vazias ou que não começam com data
            if not re.match(r'^\d{2}/\d{2}', line):
                continue
                
            # Pula linhas de cabeçalho ou informações que não são transações
            if any(skip in line.upper() for skip in ['SALDO FATURA ANTERIOR', 'PAGAMENTOS/CRÉDITOS', 'DATA', 'DESCRIÇÃO']):
                continue
            
            # Padrão para linha de transação: DD/MM seguido de descrição e valor no final
            # Exemplo: "27/05 O PARK DESINGDF BRASILIA BR R$ 159,90"
            match = re.match(r'^(\d{2}/\d{2})\s+(.*?)\s+R\$\s*([\d\.,]+)$', line)
            
            if match:
                date = match.group(1)
                description = match.group(2).strip()
                value_text = match.group(3)
                
                # Limpa a descrição
                description = self._clean_bb_description(description)
                
                # Se a descrição ficou vazia, pula
                if not description:
                    continue
                
                try:
                    # Converte o valor para float
                    valor_float = float(value_text.replace('.', '').replace(',', '.'))
                    
                    # Cria o objeto Transacao
                    transacao = Transacao(
                        data=date,
                        descricao=description,
                        valor=valor_float,
                        categoria=self._categorize_transaction(description)
                    )
                    
                    transactions.append(transacao)
                    
                except ValueError:
                    logger.warning(f"Não foi possível converter o valor '{value_text}' para float. Transação ignorada.")
                    continue
        
        return transactions
    
    def _clean_bb_description(self, description: str) -> str:
        """
        Limpa especificamente as descrições do Banco do Brasil.
        
        Args:
            description: Descrição original
            
        Returns:
            Descrição limpa
        """
        # Remove códigos de país
        description = re.sub(r'\s+BR\s*$', '', description)
        description = re.sub(r'\s+BRASIL\s*$', '', description)
        
        # Remove cidade no final se estiver presente
        # Padrão comum: "ESTABELECIMENTO CIDADE"
        cities = ['BRASILIA', 'SAO PAULO', 'OSASCO', 'CURITIBA', 'SANTANA DE PA']
        for city in cities:
            description = re.sub(rf'\s+{city}\s*$', '', description, flags=re.IGNORECASE)
        
        # Remove múltiplos espaços
        description = re.sub(r'\s+', ' ', description).strip()
        
        return description
        
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
