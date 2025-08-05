import json
import pandas as pd
from typing import Dict, Any, Optional, List
import os
import logging
from datetime import datetime
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
                    'Campo': ['Titular', 'Número do Cartão', 'Data de Fechamento', 'Data de Vencimento', 'Valor Total', 'Banco', 'Data de Processamento'],
                    'Valor': [
                        data.get('titular', 'Não informado'),
                        data.get('numero_cartao', 'Não informado'),
                        data.get('data_fechamento', 'Não informado'),
                        data.get('data_vencimento', 'Não informado'),
                        data.get('valor_total', 'Não informado'),
                        data.get('banco', 'Não informado'),
                        data.get('data_processamento', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    ]
                }
                
                resumo_df = pd.DataFrame(resumo)
                resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Planilha de transações
                if data.get('transacoes') and len(data['transacoes']) > 0:
                    transacoes_df = pd.DataFrame(data['transacoes'])
                    transacoes_df.to_excel(writer, sheet_name='Transações', index=False)
                    
                    # Adiciona uma planilha de análise por categorias (se houver)
                    self._add_category_analysis(writer, data.get('transacoes', []))
                else:
                    # Se não há transações, cria uma planilha vazia
                    empty_df = pd.DataFrame({'Mensagem': ['Nenhuma transação encontrada']})
                    empty_df.to_excel(writer, sheet_name='Transações', index=False)
            
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
        # Verifica se há transações
        if not transacoes:
            return
            
        try:
            # Cria DataFrame
            df = pd.DataFrame(transacoes)
            
            # Verifica se existe a coluna categoria
            if 'categoria' not in df.columns:
                df['categoria'] = 'Não Categorizado'
            
            # Verifica se existe a coluna valor
            if 'valor' not in df.columns:
                return
            
            # Substitui valores None por 'Não Categorizado'
            df['categoria'].fillna('Não Categorizado', inplace=True)
            
            # Agrupa por categoria e soma os valores
            categoria_df = df.groupby('categoria')['valor'].agg(['sum', 'count']).reset_index()
            categoria_df.columns = ['Categoria', 'Valor Total', 'Quantidade']
            
            # Ordena por valor total (decrescente)
            categoria_df = categoria_df.sort_values(by='Valor Total', ascending=False)
            
            # Adiciona ao Excel
            categoria_df.to_excel(writer, sheet_name='Análise por Categoria', index=False)
            
        except Exception as e:
            logger.warning(f"Não foi possível gerar a análise por categorias: {str(e)}")
            # Se falhar, não interrompe o processo, apenas não adiciona a planilha
    
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
