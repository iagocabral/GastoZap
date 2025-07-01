# Assistente Financeiro - Extrator de Faturas de Cartão de Crédito

O projeto foi desenvolvido com uma arquitetura modular e de fácil manutenção, utilizando FastAPI para criar uma API robusta que extrai dados de faturas de cartão de crédito em PDF e os disponibiliza em formatos JSON ou Excel.

Estrutura do Projeto
```
assistente-financeiro/
├── app/
│   ├── api/            - Definições da API (rotas, endpoints)
│   ├── core/           - Configurações e funções essenciais
│   ├── models/         - Modelos de dados
│   ├── schemas/        - Esquemas de validação (Pydantic)
│   ├── services/       - Serviços (extração de PDF, exportação de dados)
│   ├── static/         - Arquivos estáticos e exportados
│   ├── templates/      - Templates para possível interface web
│   └── utils/          - Funções utilitárias
├── tests/              - Testes automatizados
└── main.py             - Ponto de entrada da aplicação
```
