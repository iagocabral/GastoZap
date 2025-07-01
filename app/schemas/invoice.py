from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Transacao(BaseModel):
    """Esquema para representar uma transação na fatura"""
    data: str = Field(..., description="Data da transação (DD/MM)")
    descricao: str = Field(..., description="Descrição do estabelecimento")
    valor: float = Field(..., description="Valor da transação")

class FaturaCartao(BaseModel):
    """Esquema para representar os dados extraídos de uma fatura de cartão de crédito"""
    titular: Optional[str] = Field(None, description="Nome do titular do cartão")
    numero_cartao: Optional[str] = Field(None, description="Número do cartão (mascarado)")
    data_fechamento: Optional[str] = Field(None, description="Data de fechamento da fatura")
    valor_total: Optional[str] = Field(None, description="Valor total da fatura")
    transacoes: List[Transacao] = Field(default_factory=list, description="Lista de transações")

class ExportRequest(BaseModel):
    """Esquema para solicitação de exportação"""
    export_format: str = Field("json", description="Formato de exportação (json ou excel)")
