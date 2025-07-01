import os
import pytest
import json
import tempfile
from app.services.pdf_extractor import PDFExtractor
from app.services.data_exporter import DataExporter

# Dados de exemplo para os testes
SAMPLE_DATA = {
    "titular": "NOME DO CLIENTE",
    "numero_cartao": "****1234",
    "data_fechamento": "15/06/2025",
    "valor_total": "1500.00",
    "data_processamento": "2025-07-01 10:30:00",
    "transacoes": [
        {
            "data": "01/06",
            "descricao": "SUPERMERCADO XYZ",
            "valor": 150.00,
            "categoria": "Supermercado"
        },
        {
            "data": "05/06",
            "descricao": "RESTAURANTE ABC",
            "valor": 85.50,
            "categoria": "Alimentação"
        },
        {
            "data": "10/06",
            "descricao": "FARMACIA 123",
            "valor": 45.75,
            "categoria": "Saúde"
        }
    ]
}


class TestDataExporter:
    """Testes para o serviço de exportação de dados"""
    
    @pytest.fixture
    def exporter(self):
        """Fixture para criar uma instância do exportador com diretório temporário"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield DataExporter(output_dir=temp_dir)
    
    def test_to_json(self, exporter):
        """Testa a exportação para JSON"""
        result_path = exporter.to_json(SAMPLE_DATA, "test_output.json")
        
        # Verifica se o arquivo foi criado
        assert os.path.exists(result_path)
        
        # Verifica se o conteúdo é válido
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        assert data["titular"] == SAMPLE_DATA["titular"]
        assert len(data["transacoes"]) == len(SAMPLE_DATA["transacoes"])
    
    def test_to_excel(self, exporter):
        """Testa a exportação para Excel"""
        import pandas as pd
        
        result_path = exporter.to_excel(SAMPLE_DATA, "test_output.xlsx")
        
        # Verifica se o arquivo foi criado
        assert os.path.exists(result_path)
        
        # Verifica se o conteúdo é válido
        try:
            # Lê a planilha de resumo
            df_resumo = pd.read_excel(result_path, sheet_name="Resumo")
            assert not df_resumo.empty
            
            # Lê a planilha de transações
            df_transacoes = pd.read_excel(result_path, sheet_name="Transações")
            assert len(df_transacoes) == len(SAMPLE_DATA["transacoes"])
            
        except Exception as e:
            pytest.fail(f"Erro ao ler o arquivo Excel: {str(e)}")
            
    def test_generate_report(self, exporter):
        """Testa a geração de relatório"""
        # Teste com JSON
        json_path = exporter.generate_report(SAMPLE_DATA, "json")
        assert os.path.exists(json_path)
        assert json_path.endswith(".json")
        
        # Teste com Excel
        excel_path = exporter.generate_report(SAMPLE_DATA, "excel")
        assert os.path.exists(excel_path)
        assert excel_path.endswith(".xlsx")
