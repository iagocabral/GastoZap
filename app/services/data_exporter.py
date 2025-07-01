import json
import pandas as pd
from typing import Dict, Any, Optional, List
import os
import logging
from datetime import datetime
from app.utils.pdf_utils import format_currency
from app.core.config import EXPORTS_DIR

logger = logging.getLogger(__name__)

class DataExporter:
    """
    Classe responsável por exportar os dados extraídos para diferentes formatos.
    """
    
    def __init__(self, output_dir: str = EXPORTS_DIR):
        """
        Inicializa o exportador de dados.
        
        Args:
            output_dir: Diretório onde os arquivos exportados serão salvos
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def to_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        Exporta os dados para JSON.
        
        Args:
            data: Dados a serem exportados
            filename: Nome do arquivo de saída
            
        Returns:
            Caminho para o arquivo exportado
        """
        try:
            output_path = os.path.join(self.output_dir, filename)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                
            logger.info(f"Dados exportados para JSON: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Erro ao exportar para JSON: {str(e)}")
            raise
    
    def to_excel(self, data: Dict[str, Any], filename: str) -> str:
        """
        Exporta os dados para Excel.
        
        Args:
            data: Dados a serem exportados
            filename: Nome do arquivo de saída
            
        Returns:
            Caminho para o arquivo exportado
        """
        try:
            output_path = os.path.join(self.output_dir, filename)
            
            # Cria um Excel com múltiplas planilhas
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Planilha de resumo
                resumo = {
                    'Titular': [data.get('titular', 'Não informado')],
                    'Número do Cartão': [data.get('numero_cartao', 'Não informado')],
                    'Data de Fechamento': [data.get('data_fechamento', 'Não informado')],
                    'Valor Total': [format_currency(float(data.get('valor_total', '0')))],
                    'Data de Processamento': [data.get('data_processamento', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],
                }
                pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo', index=False)
                
                # Planilha de transações
                if data.get('transacoes'):
                    transacoes_df = pd.DataFrame(data['transacoes'])
                    
                    # Formatação das colunas
                    if 'valor' in transacoes_df.columns:
                        transacoes_df['valor'] = transacoes_df['valor'].apply(lambda x: format_currency(x))
                    
                    transacoes_df.to_excel(writer, sheet_name='Transações', index=False)
                
                # Adiciona uma planilha de análise por categorias (se houver)
                self._add_category_analysis(writer, data.get('transacoes', []))
            
            logger.info(f"Dados exportados para Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {str(e)}")
            raise
    
    def _add_category_analysis(self, writer: pd.ExcelWriter, transacoes: List[Dict[str, Any]]) -> None:
        """
        Adiciona uma planilha com análise por categorias.
        
        Args:
            writer: ExcelWriter aberto
            transacoes: Lista de transações
        """
        # Verifica se há transações e se possuem a propriedade categoria
        if not transacoes or 'categoria' not in transacoes[0]:
            return
            
        # Cria DataFrame
        df = pd.DataFrame(transacoes)
        
        # Agrupa por categoria e soma os valores
        try:
            categoria_df = df.groupby('categoria', dropna=False)['valor'].agg(['sum', 'count'])
            categoria_df.columns = ['Valor Total', 'Quantidade']
            categoria_df = categoria_df.reset_index()
            
            # Renomeia categoria None para 'Não Categorizado'
            categoria_df['categoria'].fillna('Não Categorizado', inplace=True)
            
            # Formata o valor
            categoria_df['Valor Total'] = categoria_df['Valor Total'].apply(lambda x: format_currency(x))
            
            # Ordena por valor total (decrescente)
            categoria_df = categoria_df.sort_values(by='Valor Total', ascending=False)
            
            # Renomeia as colunas
            categoria_df.rename(columns={'categoria': 'Categoria'}, inplace=True)
            
            # Adiciona ao Excel
            categoria_df.to_excel(writer, sheet_name='Análise por Categoria', index=False)
            
        except Exception as e:
            logger.warning(f"Não foi possível gerar a análise por categorias: {str(e)}")
    
    def generate_report(self, data: Dict[str, Any], output_format: str = "json") -> str:
        """
        Gera um relatório no formato especificado.
        
        Args:
            data: Dados para o relatório
            output_format: Formato de saída ("json" ou "excel")
            
        Returns:
            Caminho para o arquivo gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format.lower() == "excel":
            filename = f"fatura_report_{timestamp}.xlsx"
            return self.to_excel(data, filename)
        else:  # json por padrão
            filename = f"fatura_report_{timestamp}.json"
            return self.to_json(data, filename)
