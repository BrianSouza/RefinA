# RefinA - Refinamento Ágil com LLMs

O **RefinA** é uma aplicação projetada para otimizar o fluxo de refinamento ágil de desenvolvimento de software utilizando Inteligência Artificial (LLMs). Ele orquestra um fluxo de dois agentes especializados:

1. **Agent PO (Product Owner)**: Analisa o pedido do usuário (User Story ou problema), cruza com a documentação de apoio fornecida e o contexto do sistema, e elabora uma User Story robusta, validando se está pronta para entrar em desenvolvimento.
2. **Agent Dev (Engenharia)**: Atua sobre a User Story aprovada pelo Agent PO e faz o refinamento técnico, quebrando o problema em tarefas técnicas detalhadas de Frontend e Backend, além de mapear riscos, camadas impactadas e ambiguidades.

A interface do usuário é construída em **Streamlit**, permitindo uma experiência interativa, visualização do progresso dos agentes, captura de métricas de uso e inserção dinâmica de links ou textos de documentação.

---

## 🛠️ Requisitos

- Python 3.9+
- Uma chave de API para o modelo configurado (ex: OpenAI, Anthropic, local via Ollama, etc.)

---

## 🚀 Como Instalar

1. **Clone ou acesse o repositório** na sua máquina local.

2. **Crie e ative um ambiente virtual** (recomendado):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências** do projeto navegando até a raiz do projeto e rodando:
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Configure as Variáveis de Ambiente**:
   - Faça uma cópia do arquivo `.env.exemplo` para `.env` na raiz do projeto:
     ```bash
     cp .env.exemplo .env
     ```
   - Edite o arquivo `.env` inserindo suas chaves de API (por exemplo, `OPENAI_API_KEY`) e configurando o modelo a ser utilizado pelos Agentes (conforme a configuração do `pydantic-ai`).

---

## 💻 Como Executar

A interface interativa é inicializada através do **Streamlit** e a integração com o repositório exige a inicialização da API **FastAPI**.

Como não estamos utilizando scripts automáticos, você precisará abrir dois terminais (linhas de comando) diferentes na raiz do seu projeto (`c:\Projetos\RefinA`).

**Terminal 1: Iniciando a API do Azure DevOps:**
```bash
uvicorn api.ado_api:app --reload --port 8000
```
*(Deixe esta janela/terminal aberto rodando. Você verá mensagens informando que a aplicação subiu ("Application startup complete").)*

**Terminal 2: Iniciando o Frontend (Streamlit):**
```bash
streamlit run app/main.py
```
*(Ao rodar este comando, seu navegador padrão abrirá automaticamente a aplicação em `http://localhost:8501`. Mantenha esta janela também aberta enquanto usar o app.)*

### Utilizando a Interface
1. **Descreva o Problema**: Preencha o campo obrigatório com o que o usuário deseja (User Story bruta).
2. **Contexto (Opcional)**: Informe os detalhes ou a arquitetura do projeto.
3. **Anexos**: Você pode adicionar até 5 links (URLs que o sistema irá extrair automaticamente) ou colar textos diretos de regras de negócio.
4. **Criação e Refinamento**: 
   - Ao iniciar, o Agent PO criará a Story detalhada.
   - Pela interface, você acompanha métricas de tempo e custo (tokens).
   - Caso o PO sinalize que a história não está boa, você pode arrumar o texto gerado ou forçar o refinamento.
   - O Agent Dev, em seguida, construirá as tarefas de tecnologia prontas para implementação!
