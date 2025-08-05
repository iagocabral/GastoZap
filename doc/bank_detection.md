# Guia de uso: Detecção Automática de Banco

Este documento descreve como utilizar as funcionalidades de detecção automática de banco no Assistente Financeiro.

## Visão Geral

O Assistente Financeiro agora suporta a detecção automática do banco emissor da fatura de cartão de crédito. Isso permite que o sistema utilize padrões específicos de extração para cada banco, melhorando a precisão e confiabilidade dos dados extraídos.

## Bancos Suportados

Atualmente, os seguintes bancos são suportados:

- Banco do Brasil (completo)
- Nubank (parcial)
- Itaú (parcial)
- Bradesco (parcial)
- Santander (parcial)

## Como Funciona

O sistema utiliza uma combinação de expressões regulares e padrões específicos para identificar o banco emissor com base no conteúdo da fatura. Uma vez identificado o banco, o sistema seleciona os padrões de extração apropriados para extrair os dados corretamente.

## Uso via API

### Listar Bancos Disponíveis

```
GET /banks/
```

**Resposta:**
```json
{
  "banks": {
    "banco_do_brasil": "Banco do Brasil",
    "nubank": "Nubank",
    "itau": "Itaú",
    "bradesco": "Bradesco",
    "santander": "Santander"
  }
}
```

### Detectar Banco de uma Fatura

```
POST /detect-bank/
```

**Parâmetros:**
- `file`: Arquivo PDF da fatura (multipart/form-data)

**Resposta:**
```json
{
  "detected": true,
  "bank_id": "banco_do_brasil",
  "bank_name": "Banco do Brasil"
}
```

### Processar Fatura com Banco Específico

```
POST /upload-invoice/
```

**Parâmetros:**
- `file`: Arquivo PDF da fatura (multipart/form-data)
- `export_format`: Formato de exportação (json ou excel) (opcional, padrão: json)
- `bank_id`: ID do banco emissor da fatura (opcional)

Se o `bank_id` não for especificado, o sistema tentará detectar automaticamente o banco.

## Uso via Utilitários

### Teste de Detecção de Banco

Para testar a detecção de banco em uma fatura:

```bash
python app/utils/test_bank_detection.py <caminho_do_pdf>
```

### Análise de Fatura do Banco do Brasil

Para analisar uma fatura do Banco do Brasil e identificar padrões:

```bash
python app/utils/analyze_bb_invoice.py <caminho_do_pdf>
```

## Adicionando Suporte a Novos Bancos

Para adicionar suporte a um novo banco:

1. Adicione os padrões de detecção no `app/utils/bank_detector.py`:
   ```python
   BANK_PATTERNS = {
       'novo_banco': [
           r'Padrão 1',
           r'Padrão 2'
       ]
   }
   ```

2. Adicione os padrões de extração no `app/services/pdf_extractor.py`:
   ```python
   BANK_EXTRACTORS = {
       'novo_banco': {
           'titular': r"Padrão para titular",
           'numero_cartao': r"Padrão para número do cartão",
           # etc.
       }
   }
   ```

3. Teste com faturas reais do banco usando o utilitário de teste.
