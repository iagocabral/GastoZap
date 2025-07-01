import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Testa o endpoint de health check"""
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_invalid_file_type():
    """Testa o upload de um arquivo que não é PDF"""
    # Cria um arquivo de texto simples
    with open("test_file.txt", "w") as f:
        f.write("Este não é um PDF")

    # Faz o upload
    files = {"file": ("test_file.txt", open("test_file.txt", "rb"), "text/plain")}
    response = client.post("/api/upload-invoice/", files=files, data={"export_format": "json"})

    # Limpa o arquivo de teste
    import os
    os.remove("test_file.txt")

    # Verifica a resposta
    assert response.status_code == 400
    assert "Apenas arquivos PDF são aceitos" in response.text


def test_invalid_export_format():
    """Testa o upload com um formato de exportação inválido"""
    # Simula um PDF
    files = {"file": ("fake.pdf", b"%PDF-1.7\n", "application/pdf")}
    response = client.post("/api/upload-invoice/", files=files, data={"export_format": "csv"})
    
    assert response.status_code == 400
    assert "Formato de exportação deve ser 'json' ou 'excel'" in response.text
