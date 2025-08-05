from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form, Query
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import pandas as pd
from typing import Optional, List, Dict
from pydantic import ValidationError

from app.services.pdf_extractor import PDFExtractor
from app.services.data_exporter import DataExporter
from app.utils.pdf_utils import cleanup_temp_files
from app.utils.bank_detector import BankDetector
from app.schemas.invoice import ExportRequest, FaturaCartao

router = APIRouter()

@router.post("/upload-invoice/")
async def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    export_format: str = Form("json"),
    bank_id: Optional[str] = Form(None)
):
    """
    Endpoint para upload de faturas de cartão em PDF.
    Retorna os dados extraídos no formato especificado (json ou excel).
    
    Args:
        background_tasks: Tarefas em segundo plano
        file: Arquivo PDF da fatura
        export_format: Formato de exportação (json ou excel)
        bank_id: ID do banco emissor da fatura (opcional)
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")
    
    if export_format not in ["json", "excel"]:
        raise HTTPException(status_code=400, detail="Formato de exportação deve ser 'json' ou 'excel'")
    
    # Gera um ID único para este processamento
    process_id = str(uuid.uuid4())
    
    # Salva o arquivo temporariamente
    temp_path = os.path.join("app/static/uploads", f"temp_{process_id}.pdf")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Se o banco não foi especificado, tenta detectá-lo automaticamente
        if not bank_id:
            detected_bank = BankDetector.detect_bank(temp_path)
            if detected_bank:
                bank_id = detected_bank
        
        # Extrai os dados do PDF
        extractor = PDFExtractor()
        extracted_data = extractor.extract(temp_path, bank_id)
        
        # Valida os dados extraídos
        try:
            # Converte para o modelo Pydantic para validação
            fatura_schema = FaturaCartao(**extracted_data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Dados extraídos inválidos: {str(e)}")
        
        # Exporta os dados para o formato solicitado
        exporter = DataExporter()
        
        if export_format == "json":
            result_path = exporter.to_json(extracted_data, f"invoice_{process_id}.json")
            return JSONResponse(content=extracted_data)
        else:  # excel
            result_path = exporter.to_excel(extracted_data, f"invoice_{process_id}.xlsx")
            
            # Adiciona tarefa para limpar o arquivo de resultado após um tempo
            background_tasks.add_task(cleanup_temp_files, [result_path])
            
            return FileResponse(
                path=result_path, 
                filename=f"invoice_data_{process_id}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
    
    finally:
        # Adiciona tarefa para limpar os arquivos temporários
        background_tasks.add_task(cleanup_temp_files, [temp_path])

@router.get("/health/")
async def health_check():
    """Endpoint para verificar a saúde da aplicação"""
    return {"status": "ok", "version": "0.1.0"}
    
@router.get("/banks/")
async def list_banks():
    """
    Retorna a lista de bancos disponíveis para extração de faturas.
    """
    available_banks = BankDetector.get_available_banks()
    return {"banks": available_banks}
    
@router.post("/detect-bank/")
async def detect_bank(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Detecta o banco emissor de uma fatura de cartão em PDF.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")
    
    # Gera um ID único para este processamento
    process_id = str(uuid.uuid4())
    
    # Salva o arquivo temporariamente
    temp_path = os.path.join("app/static/uploads", f"temp_{process_id}.pdf")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Detecta o banco
        bank_id = BankDetector.detect_bank(temp_path)
        available_banks = BankDetector.get_available_banks()
        
        if bank_id:
            bank_name = available_banks.get(bank_id, bank_id)
            return {"detected": True, "bank_id": bank_id, "bank_name": bank_name}
        else:
            return {"detected": False, "message": "Não foi possível identificar o banco emissor da fatura"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")
    
    finally:
        # Adiciona tarefa para limpar os arquivos temporários
        background_tasks.add_task(cleanup_temp_files, [temp_path])
    
@router.post("/batch-process/")
async def batch_process(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    export_format: str = Form("excel")
):
    """
    Endpoint para processar múltiplas faturas de uma vez.
    Retorna um arquivo com os dados consolidados.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    
    if export_format not in ["json", "excel"]:
        raise HTTPException(status_code=400, detail="Formato de exportação deve ser 'json' ou 'excel'")
    
    # Gera um ID único para este processamento
    batch_id = str(uuid.uuid4())
    
    # Lista para armazenar os caminhos dos arquivos temporários
    temp_files = []
    
    try:
        all_data = []
        
        # Processa cada arquivo
        for idx, file in enumerate(files):
            if not file.filename.lower().endswith('.pdf'):
                continue
                
            # Salva o arquivo temporariamente
            temp_path = os.path.join("app/static/uploads", f"temp_{batch_id}_{idx}.pdf")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                
            temp_files.append(temp_path)
            
            # Extrai os dados do PDF
            try:
                extractor = PDFExtractor()
                extracted_data = extractor.extract(temp_path)
                all_data.append(extracted_data)
            except Exception as e:
                # Registra o erro mas continua processando os outros arquivos
                print(f"Erro ao processar {file.filename}: {str(e)}")
        
        if not all_data:
            raise HTTPException(status_code=400, detail="Nenhum arquivo válido para processar")
        
        # Exporta os dados consolidados
        exporter = DataExporter()
        
        if export_format == "json":
            # Para JSON, retorna uma lista de resultados
            result_path = exporter.to_json({"faturas": all_data}, f"batch_{batch_id}.json")
            return JSONResponse(content={"faturas": all_data})
        else:  # excel
            # Para Excel, cria um arquivo com múltiplas planilhas (uma para cada fatura)
            # A implementação atual do exporter precisa ser adaptada para isso
            result_path = os.path.join("app/static/exports", f"batch_{batch_id}.xlsx")
            
            # Cria um Excel com múltiplas planilhas
            with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
                for idx, data in enumerate(all_data):
                    # Identificador para esta fatura
                    sheet_name = f"Fatura {idx + 1}"
                    
                    # Resumo da fatura
                    resumo = {
                        'Titular': [data.get('titular', '')],
                        'Número do Cartão': [data.get('numero_cartao', '')],
                        'Data de Fechamento': [data.get('data_fechamento', '')],
                        'Valor Total': [data.get('valor_total', '')],
                    }
                    pd.DataFrame(resumo).to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Transações da fatura
                    if data.get('transacoes'):
                        transacoes_df = pd.DataFrame(data['transacoes'])
                        transacoes_df.to_excel(writer, sheet_name=f"{sheet_name} - Transações", index=False)
            
            # Adiciona tarefa para limpar o arquivo de resultado após um tempo
            background_tasks.add_task(cleanup_temp_files, [result_path])
            
            return FileResponse(
                path=result_path, 
                filename=f"batch_invoices_{batch_id}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    finally:
        # Adiciona tarefa para limpar os arquivos temporários
        background_tasks.add_task(cleanup_temp_files, temp_files)

@router.get("/bank-patterns/{bank_id}")
async def get_bank_patterns(bank_id: str):
    """
    Retorna os padrões de expressão regular específicos de um banco para extração de faturas.
    
    Args:
        bank_id: ID do banco
    """
    extractor = PDFExtractor()
    
    if bank_id in extractor.BANK_EXTRACTORS:
        return {"bank_id": bank_id, "patterns": extractor.BANK_EXTRACTORS[bank_id]}
    else:
        available_banks = list(extractor.BANK_EXTRACTORS.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Banco não encontrado. Bancos disponíveis: {available_banks}"
        )
