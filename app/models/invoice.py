from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Transacao:
    """Classe para representar uma transação na fatura"""
    data: str
    descricao: str
    valor: float
    categoria: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            "data": self.data,
            "descricao": self.descricao,
            "valor": self.valor,
            "categoria": self.categoria
        }


@dataclass
class Fatura:
    """Classe para representar uma fatura de cartão de crédito"""
    titular: Optional[str] = None
    numero_cartao: Optional[str] = None
    data_fechamento: Optional[str] = None
    data_vencimento: Optional[str] = None
    valor_total: Optional[str] = None
    banco: Optional[str] = None
    transacoes: List[Transacao] = field(default_factory=list)
    data_processamento: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def adicionar_transacao(self, transacao: Transacao) -> None:
        """Adiciona uma transação à fatura"""
        self.transacoes.append(transacao)
        
    def calcular_total(self) -> float:
        """Calcula o valor total da fatura com base nas transações"""
        return sum(t.valor for t in self.transacoes)
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            "titular": self.titular,
            "numero_cartao": self.numero_cartao,
            "data_fechamento": self.data_fechamento,
            "data_vencimento": self.data_vencimento,
            "valor_total": self.valor_total,
            "banco": self.banco,
            "data_processamento": self.data_processamento,
            "transacoes": [t.to_dict() for t in self.transacoes]
        }
