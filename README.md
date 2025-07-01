# Assistente Financeiro

Uma API para extração de dados de faturas de cartão de crédito em PDF e exportação para JSON ou Excel.

## Funcionalidades

- Upload de faturas de cartão de crédito em PDF
- Extração automática de informações como titular, número do cartão, data de fechamento, valor total e transações
- Categorização automática de transações
- Exportação dos dados para JSON ou Excel
- Processamento em lote de múltiplas faturas

## Estrutura do Projeto

```
assistente-financeiro/
├── app/
│   ├── api/            - Definições da API (rotas, endpoints)
│   ├── core/           - Configurações e funcionalidades centrais
│   ├── models/         - Modelos de dados
│   ├── schemas/        - Esquemas de validação (Pydantic)
│   ├── services/       - Serviços (extração de PDF, exportação de dados)
│   ├── static/         - Arquivos estáticos (resultados de exportação)
│   ├── templates/      - Templates para interface web (se implementada)
│   └── utils/          - Funções utilitárias
├── tests/              - Testes automatizados
└── main.py             - Ponto de entrada da aplicação
```

## Requisitos

- Python 3.7+
- FastAPI
- PyPDF2
- Pandas
- Pydantic
- Uvicorn

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd assistente-financeiro
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Para executar a API localmente:

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Documentação da API

A documentação interativa da API estará disponível em:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exemplos de Uso

### Upload de uma Fatura

```bash
curl -X POST "http://localhost:8000/api/upload-invoice/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@caminho/para/fatura.pdf" \
  -F "export_format=json"
```

### Processamento em Lote

```bash
curl -X POST "http://localhost:8000/api/batch-process/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@caminho/para/fatura1.pdf" \
  -F "files=@caminho/para/fatura2.pdf" \
  -F "export_format=excel"
```

## Limitações

- O sistema está configurado para reconhecer padrões específicos de faturas. Pode ser necessário adaptar as expressões regulares para diferentes formatos de fatura.
- O processo de categorização automática é básico e pode precisar de melhorias para maior precisão.

## Próximos Passos

- Implementar interface web para upload e visualização de faturas
- Melhorar o algoritmo de categorização usando machine learning
- Adicionar suporte para mais formatos de fatura
- Implementar autenticação e multi-usuário
- Adicionar suporte para análise histórica de gastos
