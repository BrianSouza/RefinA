# 🤖 RefinA — Refinamento Ágil com IA

O **RefinA** é uma plataforma de refinamento ágil assistida por Inteligência Artificial. Ela automatiza o processo de transformar pedidos informais de funcionalidades em **User Stories** prontas para desenvolvimento e **Tarefas Técnicas** detalhadas, eliminando gargalos de comunicação entre Product Owner e Engenharia.

## O que o RefinA faz?

Em um fluxo ágil tradicional, transformar uma demanda vaga em tarefas técnicas implementáveis exige múltiplas reuniões de refinamento. O RefinA acelera esse processo com **dois agentes de IA especializados** que trabalham em pipeline:

| Etapa | Agente | O que faz |
|-------|--------|-----------|
| **1** | 🧑‍💼 **Agent PO** | Recebe o pedido bruto do usuário, cruza com a documentação de apoio e o contexto do projeto, e gera uma **User Story completa** (com critérios de aceite, score de incerteza e críticas, se houver). |
| **2** | 👩‍💻 **Agent Dev** | Atua sobre a User Story aprovada e produz o **refinamento técnico**: tarefas de Frontend e Backend, camadas impactadas, análise de risco e instruções detalhadas (*prompt for AI*) para cada tarefa. |

Ao final, as stories e tasks podem ser **exportadas diretamente para o Azure DevOps** via integração nativa.

---

## 🏗️ Arquitetura em Alto Nível

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USUÁRIO (Navegador)                          │
│                      http://localhost:8501                           │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    app/main.py  (Streamlit UI)                      │
│                                                                      │
│  • Formulário de entrada (story bruta + contexto + docs)            │
│  • Visualização da Story refinada + métricas                        │
│  • Botão de exportação para Azure DevOps                            │
└──────┬───────────────────────────────────────────┬───────────────────┘
       │                                           │
       ▼                                           ▼
┌──────────────────────┐                ┌──────────────────────────────┐
│   src/agentes/        │                │  api/ado_api.py (FastAPI)    │
│                      │                │                              │
│  AgentBase (ABC)     │                │  POST /api/v1/ado/           │
│    ├─ AgentPO        │                │       create_work_items      │
│    └─ AgentDev       │                │                              │
│                      │                │  Cria Story + Tasks          │
│  Usa: pydantic-ai,   │                │  no Azure DevOps via PAT     │
│       Ollama/OpenAI  │                └──────────────────────────────┘
└──────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  LLM Provider (configurável)                        │
│                                                                      │
│   Local: Ollama (llama3.2, etc.)                                    │
│   Nuvem: OpenAI · Anthropic · Google Gemini                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Estrutura de Pastas

```
RefinA/
├── app/
│   └── main.py               # Interface Streamlit (frontend)
├── api/
│   └── ado_api.py             # API FastAPI — integração Azure DevOps
├── src/
│   ├── agentes/
│   │   ├── agent_base.py      # Classe abstrata base (configura LLM)
│   │   ├── agent_po.py        # Agente Product Owner
│   │   └── agent_dev.py       # Agente de Engenharia
│   ├── models/
│   │   ├── input_story.py     # Entrada: prompt + contexto + docs
│   │   ├── output_story.py    # Saída PO: story + is_satisfactory
│   │   ├── TechnicalRefinementOutput.py  # Saída Dev: tasks + riscos
│   │   ├── task.py            # Modelo de tarefa técnica
│   │   ├── critique.py        # Crítica sobre a story
│   │   └── attachment.py      # Documento de apoio anexado
│   ├── prompts/
│   │   ├── refina_storyprompt.txt   # System prompt do Agent PO
│   │   └── refina_taskprompt.txt    # System prompt do Agent Dev
│   ├── main.py                # Script CLI para testes rápidos
│   └── requirements.txt       # Dependências Python
├── .env.exemplo               # Template de variáveis de ambiente
├── .env                       # Suas variáveis reais (não versionado)
└── README.md
```

---

## 🛠️ Requisitos

- **Python 3.9+**
- **pip** (gerenciador de pacotes)
- Uma chave de API para o LLM desejado **ou** o [Ollama](https://ollama.com/) instalado localmente
- *(Opcional)* Personal Access Token (PAT) do **Azure DevOps** para a integração de exportação

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/RefinA.git
cd RefinA
```

### 2. Crie e ative um ambiente virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r src/requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Windows (PowerShell)
Copy-Item .env.exemplo .env

# Linux / macOS
cp .env.exemplo .env
```

Abra o `.env` no seu editor e preencha as chaves conforme a seção abaixo.

---

## 🔐 Variáveis de Ambiente (`.env`)

O arquivo `.env.exemplo` contém todas as variáveis necessárias. Abaixo está a descrição de cada uma:

### Modo de Execução

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `IS_LOCAL` | `true` | Define se o RefinA usa um modelo local (Ollama) ou um provedor de nuvem. `true` = local, `false` = nuvem. |

### Configurações Locais (quando `IS_LOCAL=true`)

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `MODEL_LOCAL` | `llama3.2` | Nome do modelo instalado no Ollama (ex: `llama3.2`, `mistral`, `codellama`). |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | URL base da API do Ollama. Não altere se estiver usando a instalação padrão. |
| `API_KEY_LOCAL` | `ollama` | Chave de API para o provedor local. O Ollama padrão aceita qualquer valor (ex: `ollama`). |

### Configurações de Nuvem (quando `IS_LOCAL=false`)

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `MODEL` | `gpt-4o` | Nome do modelo a usar. Deve corresponder ao provedor cuja API Key foi preenchida (ex: `gpt-4o` para OpenAI, `claude-3-opus-20240229` para Anthropic). |
| `OPENAI_API_KEY` | `sk-...` | Chave de API da **OpenAI**. Obtenha em [platform.openai.com](https://platform.openai.com/api-keys). |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Chave de API da **Anthropic**. Obtenha em [console.anthropic.com](https://console.anthropic.com/). |
| `GEMINI_API_KEY` | `AIza...` | Chave de API do **Google Gemini**. Obtenha em [aistudio.google.com](https://aistudio.google.com/apikey). |

> **Nota:** Preencha apenas a chave do provedor que você for utilizar. As demais podem ser deixadas em branco.

### Observabilidade

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `LOGFIRE_API_KEY` | `pylf_...` | Token de autenticação do [Pydantic Logfire](https://logfire.pydantic.dev/). Usado para instrumentação, rastreamento de chamadas LLM e métricas. Opcional — se não configurar, os traces não serão enviados. |

### Integração Azure DevOps

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `ADO_ORGANIZATION_URL` | `https://dev.azure.com/MinhaOrg` | URL da sua organização no Azure DevOps. |
| `ADO_PROJECT_NAME` | `MeuProjeto` | Nome do projeto dentro da organização onde as User Stories e Tasks serão criadas. |
| `ADO_PAT_KEY` | `ey...` | Personal Access Token (PAT) com permissão de **Work Items (Read & Write)**. Gere em `https://dev.azure.com/{org}/_usersettings/tokens`. |
| `ADO_API_URL` | `http://localhost:8000/api/v1/ado/create_work_items` | URL do endpoint da API FastAPI do RefinA. Não altere se estiver rodando localmente na porta padrão. |

---

## 💻 Como Executar

O RefinA é composto por dois processos que rodam em paralelo:

### Terminal 1 — API FastAPI (integração Azure DevOps)

```bash
uvicorn api.ado_api:app --reload --port 8000
```

> Aguarde a mensagem `Application startup complete`. Mantenha este terminal aberto.

### Terminal 2 — Interface Streamlit

```bash
streamlit run app/main.py
```

> O navegador abrirá automaticamente em `http://localhost:8501`.

---

## 📋 Exemplo de Uso

### 1. Descreva o problema

Na interface, preencha o campo obrigatório com a demanda. Exemplo:

> *"Quero evoluir a feature de consulta de CEP. Se durante a pesquisa o CEP não for encontrado na base, chamar o microserviço de CEP que faz uma consulta ao site dos Correios. Se encontrado, salvar o CEP na base local."*

### 2. Adicione contexto *(opcional)*

Preencha o campo de contexto do projeto:

> *"Microserviço de Logística — Arquitetura de mensageria e SQL Server."*

### 3. Anexe documentação *(opcional)*

Adicione até **5 documentos** de apoio:
- **Links (URLs)**: o sistema extrai o conteúdo automaticamente
- **Textos**: cole diretamente regras de negócio, specs técnicas, etc.

### 4. Execute o pipeline

1. Clique em **🚀 Iniciar Criação da Story**
2. O **Agent PO** gera a User Story refinada com critérios de aceite
3. Revise a story — edite se necessário ou force o refinamento
4. Clique em **⚙️ Iniciar Refinamento**
5. O **Agent Dev** gera as tarefas técnicas com *prompt for AI*, *Definition of Done*, camadas e riscos
6. *(Opcional)* Clique em **🚀 Enviar para Azure DevOps** para exportar tudo automaticamente

### Visualização de Métricas

Em cada etapa, a interface mostra:
- ⏱ **Tempo de execução** do agente
- 📊 **Tokens utilizados** (entrada e saída)
- 🧠 **Modelo utilizado**

---

## 🧰 Stack Tecnológica

| Tecnologia | Uso |
|------------|-----|
| [pydantic-ai](https://ai.pydantic.dev/) | Framework de agentes de IA com saída estruturada |
| [Streamlit](https://streamlit.io/) | Interface web interativa |
| [FastAPI](https://fastapi.tiangolo.com/) | API REST para integração com Azure DevOps |
| [Pydantic](https://docs.pydantic.dev/) | Validação e modelagem de dados |
| [Logfire](https://logfire.pydantic.dev/) | Observabilidade e tracing de chamadas LLM |
| [Ollama](https://ollama.com/) | Provedor de modelos locais |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | Extração de conteúdo de URLs anexadas |

---

## 📄 Licença

Este projeto é de uso interno / pessoal. Consulte o autor para detalhes de licenciamento.
