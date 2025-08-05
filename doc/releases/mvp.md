## Priorização de Requisitos do MVP

Use os checkboxes para marcar o que já foi feito:

- [ ] 1. **Upload e extração de faturas (API)**
- [ ] 2. **Exportação dos dados (JSON/Excel)**
- [ ] 3. **Autenticação de usuário (JWT)**
- [ ] 4. **Estrutura básica do banco de dados**
- [ ] 5. **Integração n8n com WhatsApp para upload e retorno de dados**
- [ ] 6. **Frontend simples para upload e visualização**
- [ ] 7. **Histórico de faturas por usuário**
- [ ] 8. **Deploy do sistema online**

---

## Planejamento MVP - Assistente Financeiro

### 1. Objetivo do Produto
Automatizar a extração, organização e exportação de dados de faturas de cartão de crédito, permitindo integração com WhatsApp (via n8n) e interface web para usuários.

---

### 2. Features Essenciais para o MVP

#### 2.1. Upload e Processamento de Faturas
- [ ] Upload de PDFs de faturas via API ou frontend
- [ ]  Detecção automática do banco emissor
- [ ] Extração dos dados relevantes (titular, número do cartão, data, valor, transações)
- [ ] Exportação dos dados em JSON e Excel
- [ ] Processamento em lote de múltiplos arquivos

#### 2.2. Integração com WhatsApp
- [ ] Receber PDFs via WhatsApp
- [ ] Retornar dados extraídos ou arquivos exportados diretamente pelo WhatsApp
- [ ] Autenticação do número do usuário (validação via código ou link)

#### 2.3. Interface Web (Frontend)
- [ ] Tela de login/cadastro
- [ ] Tela de upload de faturas
- [ ] Visualização dos dados extraídos
- [ ] Download dos arquivos exportados

#### 2.4. Gerenciamento de Usuários
- [ ] Cadastro e autenticação de usuários (email/senha, OAuth opcional)
- [ ] Associação de número de WhatsApp ao usuário
- [ ] Histórico de faturas processadas

#### 2.5. Outros
- [ ] Health check da API
- [ ] Listagem de bancos suportados
- [ ] Consulta de padrões de extração por banco

---

### 3. Banco de Dados

#### Requisitos
- Armazenar usuários, faturas processadas, histórico de exportações, associação com número de WhatsApp

#### Sugestão de Banco
- **PostgreSQL**: robusto, open source, ótimo suporte para dados relacionais e integrações
- Alternativa: SQLite (para protótipo local), mas PostgreSQL recomendado para produção

#### Estrutura Básica
- Tabela `users`: id, nome, email, senha (hash), whatsapp_number, data de cadastro
- Tabela `invoices`: id, user_id, dados extraídos (JSON), caminho do arquivo, data de processamento
- Tabela `exports`: id, invoice_id, tipo (json/excel), caminho do arquivo, data

---

### 4. Arquitetura do Sistema

#### Backend
- **FastAPI** (Python): APIs REST para upload, processamento, exportação, autenticação
- Serviços desacoplados para extração, exportação, integração WhatsApp
- Utilizar BackgroundTasks do FastAPI para limpeza de arquivos temporários

#### Frontend
- React, Next.js ou similar
- Comunicação via REST API

#### Integração WhatsApp
- **n8n**: automação de recebimento/envio de mensagens
- Webhook para comunicação entre n8n e backend

#### Infraestrutura
- Deploy em VPS, Heroku, Railway, ou similar
- Armazenamento de arquivos: local (para MVP), S3 ou similar para produção

---

### 5. Autenticação de Usuário

- JWT para autenticação nas APIs
- Hash de senha (bcrypt ou similar)
- Possibilidade de OAuth (Google, etc) para facilitar login
- Validação do número do WhatsApp: envio de código via WhatsApp, confirmação pelo usuário

---

### 6. Autenticação do WhatsApp no n8n

- Utilizar integração oficial do n8n com WhatsApp (ex: WhatsApp Cloud API)
- Associar número do WhatsApp ao usuário no banco de dados
- Validar número via código ou link enviado pelo bot
- Garantir que apenas usuários autenticados possam processar faturas via WhatsApp

---

### 7. Outras Considerações

- Logs de processamento e erros
- Limpeza automática de arquivos temporários
- Limite de tamanho de arquivos e quantidade de faturas por usuário
- Políticas de privacidade e segurança de dados
- Documentação da API (Swagger/OpenAPI)

---

### 8. Roadmap de MVP

1. Implementar upload e extração de faturas (API)
2. Implementar exportação (JSON/Excel)
3. Implementar autenticação de usuário (JWT)
4. Criar estrutura básica do banco de dados
5. Integrar n8n com WhatsApp para upload e retorno de dados
6. Criar frontend simples para upload e visualização
7. Implementar histórico de faturas por usuário
8. Deploy do sistema online

---

### 9. Próximos Passos para Produto

- Melhorar suporte a diferentes bancos e formatos de fatura
- Dashboard de gastos e análise financeira
- Notificações automáticas (WhatsApp/email)
- Plano de assinatura para usuários avançados

---

**Esse planejamento cobre o essencial para lançar um MVP funcional e escalável, pronto para evoluir conforme feedback dos usuários.**
