import os
import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock
from app.services.pdf_extractor import PDFExtractor
from app.services.data_exporter import DataExporter
from app.utils.bank_detector import BankDetector

# Dados de exemplo para os testes
SAMPLE_DATA = {
    "titular": "NOME DO CLIENTE",
    "numero_cartao": "****1234",
    "data_fechamento": "15/06/2025",
    "data_vencimento": "01/07/2025",
    "valor_total": "1500.00",
    "banco": "banco_do_brasil",
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


class TestBankDetector:
    """Testes para o detector de banco"""
    
    def test_get_available_banks(self):
        """Testa a obtenção dos bancos disponíveis"""
        banks = BankDetector.get_available_banks()
        
        # Verifica se há pelo menos um banco disponível
        assert len(banks) > 0
        # Verifica se o Banco do Brasil está na lista
        assert "banco_do_brasil" in banks
        
    @patch('app.utils.bank_detector.PyPDF2.PdfReader')
    def test_detect_bank(self, mock_pdf_reader):
        """Testa a detecção automática de banco"""
        # Configura o mock para retornar um texto de exemplo
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "OUROCARD INTERN. VISA-UNIV. Final 1234"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Simula um arquivo que não existe mas o mock vai interceptar a leitura
        result = BankDetector.detect_bank("fake_path.pdf")
        
        # Verifica se o banco foi corretamente identificado
        assert result == "banco_do_brasil"
        
    @patch('app.utils.bank_detector.PyPDF2.PdfReader')
    def test_detect_bank_unknown(self, mock_pdf_reader):
        """Testa a detecção automática para um banco desconhecido"""
        # Configura o mock para retornar um texto sem padrões conhecidos
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Esta é uma fatura genérica sem identificação de banco"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Simula um arquivo que não existe mas o mock vai interceptar a leitura
        result = BankDetector.detect_bank("fake_path.pdf")
        
        # Verifica que nenhum banco foi identificado
        assert result is None


class TestPDFExtractor:
    """Testes para o extrator de PDF"""
    
    @patch('app.services.pdf_extractor.PyPDF2.PdfReader')
    @patch('app.utils.pdf_utils.PDFValidator.validate_pdf')
    def test_extract_with_bank_id(self, mock_validate_pdf, mock_pdf_reader):
        """Testa a extração com um banco específico"""
        # Configura os mocks
        mock_validate_pdf.return_value = True
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Nome: CLIENTE TESTE
        Cartão: ****5678
        Fechamento: 15/06/2025
        Vencimento 01/07/2025
        Total R$ 1500,50
        
        01/06 SUPERMERCADO XYZ R$ 150,00
        05/06 RESTAURANTE ABC R$ 85,50
        """
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Testa a extração com banco específico
        extractor = PDFExtractor()
        result = extractor.extract("fake_path.pdf", bank_id="banco_do_brasil")
        
        # Verifica os dados extraídos
        assert result["banco"] == "banco_do_brasil"
        assert result["titular"] == "CLIENTE TESTE"
        assert result["numero_cartao"] == "****5678"
        assert result["data_fechamento"] == "15/06/2025"
        assert result["data_vencimento"] == "01/07/2025"
        assert result["valor_total"] == "1500,50"
        assert len(result["transacoes"]) > 0
    
    @patch('app.services.pdf_extractor.PyPDF2.PdfReader')
    @patch('app.utils.pdf_utils.PDFValidator.validate_pdf')
    @patch('app.utils.bank_detector.BankDetector.detect_bank')
    def test_extract_with_auto_detection(self, mock_detect_bank, mock_validate_pdf, mock_pdf_reader):
        """Testa a extração com detecção automática de banco"""
        # Configura os mocks
        mock_validate_pdf.return_value = True
        mock_detect_bank.return_value = "banco_do_brasil"
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Nome: CLIENTE AUTO
        Cartão: ****1234
        Fechamento: 15/06/2025
        Vencimento 01/07/2025
        Total R$ 2000,00
        
        01/06 SUPERMERCADO XYZ R$ 150,00
        05/06 RESTAURANTE ABC R$ 85,50
        """
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Testa a extração com detecção automática
        extractor = PDFExtractor()
        result = extractor.extract("fake_path.pdf")  # Sem especificar bank_id
        
        # Verifica os dados extraídos
        assert result["banco"] == "banco_do_brasil"  # Detectado automaticamente
        assert result["titular"] == "CLIENTE AUTO"
