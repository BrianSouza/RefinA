import streamlit as st
import asyncio
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Adiciona o diretório raiz ao sys.path para importar módulos de src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agentes.agent_po import AgentPO
from src.agentes.agent_dev import AgentDev
from src.models.input_story import input_story
from src.models.attachment import Attachment

st.set_page_config(page_title="RefinA - Refinamento Ágil", layout="wide")

# Helpers
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_url_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return f"Erro ao acessar URL {url}: {str(e)}"

# Inicialização de Estado
if "po_output" not in st.session_state:
    st.session_state.po_output = None
if "po_metrics" not in st.session_state:
    st.session_state.po_metrics = None
if "dev_output" not in st.session_state:
    st.session_state.dev_output = None
if "dev_metrics" not in st.session_state:
    st.session_state.dev_metrics = None
if "edited_story" not in st.session_state:
    st.session_state.edited_story = ""

async def run_po_agent(user_prompt, project_context, docs):
    agent = AgentPO()
    input_data = input_story(
        user_prompt=user_prompt,
        project_context=project_context,
        documents=docs
    )
    return await agent.run(input_data)

async def run_dev_agent(original_input_data, story_refined):
    agent = AgentDev()
    return await agent.run(original_input_data, story_refined)

st.title("RefinA - Refinamento de User Stories")

# 1. ENTRADA DE DADOS
st.header("1. Descreva o que precisa ser feito")

col1, col2 = st.columns([2, 1])

with col1:
    user_prompt = st.text_area(
        "User Story ou Problema (Obrigatório)*",
        height=150,
        placeholder="Eu como usuário gostaria de..."
    )

with col2:
    project_context = st.text_area(
        "Contexto do Sistema (Opcional)",
        height=150,
        placeholder="Microserviço de Logística - Arquitetura de mensageria e SQL Server."
    )

st.subheader("Documentação de Apoio")
st.write("Forneça links ou cole o texto de documentações (Até 5)")

docs_inputs = []
for i in range(5):
    with st.expander(f"Documento/Link {i+1}"):
        doc_type = st.radio("Tipo", ["URL", "Texto"], key=f"type_{i}", horizontal=True)
        if doc_type == "URL":
            doc_val = st.text_input("URL", key=f"url_{i}")
        else:
            doc_val = st.text_area("Texto", key=f"text_{i}", height=100)
        
        doc_name = st.text_input("Nome/Identificador (Opcional)", key=f"name_{i}")
        docs_inputs.append({"type": doc_type, "value": doc_val, "name": doc_name})

def process_attachments():
    attachments = []
    for i, doc in enumerate(docs_inputs):
        val = doc["value"].strip()
        if not val:
            continue
            
        content = ""
        if doc["type"] == "URL":
            if is_valid_url(val):
                content = fetch_url_content(val)
            else:
                st.warning(f"URL inválida no anexo {i+1}: {val}")
                continue
        else:
            content = val
            
        name = doc["name"].strip() or f"Anexo_0{i+1}"
        attachments.append(Attachment(file_name=name, content=content, file_type="reference_doc"))
    return attachments

# Botão Iniciar PO
if st.button("🚀 Iniciar Criação da Story", type="primary", use_container_width=True):
    if not user_prompt.strip():
        st.error("Por favor, preencha o campo de User Story.")
    else:
        st.session_state.po_output = None
        st.session_state.dev_output = None
        
        docs = process_attachments()
        
        with st.spinner("AgentPO está analisando a requisição e gerando a User Story... Isso pode levar alguns segundos."):
            progress_bar = st.progress(0)
            # Simula um pequeno progresso visual antes de trancar no await
            for i in range(20):
                import time
                time.sleep(0.05)
                progress_bar.progress(i)
                
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                resultado, uso, tempo = loop.run_until_complete(run_po_agent(user_prompt, project_context, docs))
                
                st.session_state.po_output = resultado
                st.session_state.po_metrics = {"uso": uso, "tempo": tempo}
                st.session_state.edited_story = resultado.story_markdown
                st.session_state.current_docs = docs
                st.session_state.current_input = user_prompt
                st.session_state.current_ctx = project_context
                progress_bar.progress(100)
                st.success("Story gerada com sucesso!")
            except Exception as e:
                progress_bar.empty()
                st.error(f"Erro durante a execução do PO: {e}")


# 2. OUTPUT DO PO
if st.session_state.po_output:
    st.divider()
    st.header("2. Story Refinada (Agent PO)")
    
    out = st.session_state.po_output
    metrics = st.session_state.po_metrics
    
    # Métricas
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Tempo de Execução", f"{metrics['tempo']:.2f}s")
    m_col2.metric("Tokens de Entrada", metrics['uso'].request_tokens)
    m_col3.metric("Tokens de Saída", metrics['uso'].response_tokens)
    
    # Propriedades
    st.subheader("Análise do Agente")
    st.write(f"**Score de Incerteza:** {out.uncertainty_score}")
    
    if out.critiques:
        st.warning("O Agente gerou as seguintes críticas/dúvidas:")
        for c in out.critiques:
            st.write(f"- **{c.field}**: {c.issue}")
    
    # Edição
    st.subheader("Conteúdo da Story")
    st.session_state.edited_story = st.text_area(
        "Edite a Story conforme necessário antes do Refinamento Técnico",
        value=st.session_state.edited_story,
        height=300
    )
    
    # Lógica de Satisfação para Refinamento
    can_refine = out.is_satisfactory
    force_refine = False
    
    if not out.is_satisfactory:
        st.error("O Agente PO considerou a Story NÃO SATISFATÓRIA.")
        force_refine = st.checkbox("FORÇAR REFINAMENTO (Li as críticas e quero prosseguir mesmo assim)")
        can_refine = force_refine
    else:
        st.success("O Agente PO considerou a Story SATISFATÓRIA para a Engenharia.")
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 RE-CRIAR Story"):
            st.session_state.po_output = None
            st.rerun()
            
    with col2:
        if st.button("⚙️ INICIAR REFINAMENTO", disabled=not can_refine, type="primary"):
            with st.spinner("AgentDev está criando as tarefas técnicas..."):
                try:
                    # Monta o input de novo com valores atuais
                    original_input = input_story(
                        user_prompt=st.session_state.current_input,
                        project_context=st.session_state.current_ctx,
                        documents=st.session_state.current_docs
                    )
                    
                    # Usa a story editada pelo usuário ou a original
                    final_story_out = st.session_state.po_output
                    final_story_out.story_markdown = st.session_state.edited_story
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    dev_res, dev_uso, dev_tempo = loop.run_until_complete(run_dev_agent(original_input, final_story_out))
                    
                    st.session_state.dev_output = dev_res
                    st.session_state.dev_metrics = {"uso": dev_uso, "tempo": dev_tempo}
                    st.success("Refinamento concluído!")
                except Exception as e:
                    st.error(f"Erro durante a execução do Dev: {e}")


# 3. OUTPUT DO DEV
if st.session_state.dev_output:
    st.divider()
    st.header("3. Tarefas Técnicas (Agent Dev)")
    
    outd = st.session_state.dev_output
    metricsd = st.session_state.dev_metrics
    
    # Métricas
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Tempo de Execução", f"{metricsd['tempo']:.2f}s")
    m_col2.metric("Tokens de Entrada", metricsd['uso'].request_tokens)
    m_col3.metric("Tokens de Saída", metricsd['uso'].response_tokens)
    
    st.subheader("Análise Técnica")
    
    st.write("**Abordagem Técnica proposta:**")
    st.write(outd.technical_approach)
    
    st.write("**Assessment de Risco:**")
    st.write(outd.risk_assessment)
    
    if outd.ambiguities:
        st.warning("**Ambiguidades encontradas:**")
        for a in outd.ambiguities:
            st.write(f"- {a}")
            
    if outd.impacted_layers:
        st.info("**Camadas impactadas:** " + ", ".join(outd.impacted_layers))
        
    st.subheader("Tasks Geradas")
    for t in outd.tasks:
        with st.expander(f"{t.title} - {t.layer} ({t.estimated_risk})"):
            st.write("**Instrução de IA (Prompt):**")
            st.write(t.prompt_for_ai)
            st.write("**Definition of Done:**")
            st.write(t.definition_of_done)
            
    if not outd.is_implementable:
        st.error("O Agente Dev indicou que as tarefas ainda NÃO SÃO IMPLEMENTÁVEIS. Responda às ambiguidades e tente novamente.")
    else:
        st.success("O Agente Dev indicou que as tarefas SÃO IMPLEMENTÁVEIS e estão prontas para o time.")
        
        st.divider()
        st.subheader("Integração com Azure DevOps")
        st.write("A exportação usará as configurações do Azure DevOps definidas no seu arquivo `.env`.")
        
        # Recupera URL da API RefinA caso configurado ou assume o padrão local
        ado_api_url = os.getenv("ADO_API_URL", "http://localhost:8000/api/v1/ado/create_work_items")

        if st.button("🚀 Enviar para Azure DevOps", type="primary", use_container_width=True):
            with st.spinner("Enviando dados para o Azure DevOps..."):
                payload = {
                    "story": {
                        "title": st.session_state.current_input[:50] + "..." if len(st.session_state.current_input) > 50 else st.session_state.current_input,
                        "description_markdown": st.session_state.edited_story
                    },
                    "tasks": [
                        {
                            "title": t.title,
                            "description": f"**Prompt:**\n{t.prompt_for_ai}\n\n**DoD:**\n{t.definition_of_done}",
                            "layer": t.layer,
                            "estimated_risk": t.estimated_risk
                        } for t in outd.tasks
                    ]
                }
                
                try:
                    resp = requests.post(ado_api_url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Sucesso! {data.get('message')}")
                        st.markdown(f"**Story Criada:** [{data['story']['id']}]({data['story']['url']})")
                        st.write(f"**Tasks Criadas:** {data.get('tasks_criadas')}")
                        for t in data.get('tasks', []):
                            if "url" in t:
                                st.markdown(f"- [{t['title']}]({t['url']})")
                            else:
                                st.warning(f"- {t['title']} (Erro: {t.get('error')})")
                    else:
                        st.error(f"Erro na integração: HTTP {resp.status_code} - {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Falha ao conectar na API local. Certifique-se de que a API do ADO (FastAPI) está rodando em {ado_api_url}")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {str(e)}")
        
    if st.button("🔄 REFINAR NOVAMENTE", use_container_width=True):
        st.session_state.dev_output = None
        st.rerun()

