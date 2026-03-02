from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
from typing import List, Optional
import base64
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="RefinA ADO Integration",
    description="API do RefinA para criação de stories e tasks no Azure DevOps",
    version="1.0.0"
)

class ADOTask(BaseModel):
    title: str = Field(description="Título da tarefa")
    description: str = Field(description="Descrição técnica detalhada (prompt, DoD, etc.)")
    layer: Optional[str] = None
    estimated_risk: Optional[str] = None

class ADOStory(BaseModel):
    title: str = Field(description="Título da User Story")
    description_markdown: str = Field(description="O conteúdo Markdown gerado pelo Agente PO")

class CreateADOItemsRequest(BaseModel):
    # Informações da Story e Tasks
    story: ADOStory
    tasks: List[ADOTask]
    
    # Customização dos tipos de Work Item, caso o processo use nomes diferentes no ADO
    work_item_type_story: str = "User Story"
    work_item_type_task: str = "Task"


def _create_work_item(url: str, pat: str, payload_patch: list) -> dict:
    """Helper para chamar a REST API do ADO e criar um Work Item com json-patch."""
    auth_bytes = f":{pat}".encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    base64_pat = base64_bytes.decode("ascii")
    
    headers = {
        "Authorization": f"Basic {base64_pat}",
        "Content-Type": "application/json-patch+json"
    }

    response = requests.post(url, json=payload_patch, headers=headers)
    
    if not response.ok:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        raise HTTPException(status_code=response.status_code, detail=f"Erro no ADO: {error_msg}")
    
    return response.json()

@app.post("/api/v1/ado/create_work_items")
def create_story_and_tasks_in_ado(data: CreateADOItemsRequest):
    """
    Recebe os dados refinados (Story + Tasks Técnicas) e os insere em um projeto do Azure DevOps.
    A comunicação é feita através de Personal Access Token (PAT) extraído do .env.
    """

    ado_org = os.getenv("ADO_ORGANIZATION_URL")
    ado_proj = os.getenv("ADO_PROJECT_NAME")
    ado_pat = os.getenv("ADO_PAT_KEY")

    if not all([ado_org, ado_proj, ado_pat]):
        raise HTTPException(status_code=500, detail="Configurações de ADO ausentes no arquivo .env (ADO_ORGANIZATION_URL, ADO_PROJECT_NAME, ADO_PAT_KEY)")

    base_url = ado_org.rstrip('/')
    project = ado_proj
    api_version = "7.1-preview.3"

    # 1. Cria a User Story
    story_url = f"{base_url}/{project}/_apis/wit/workitems/${data.work_item_type_story}?api-version={api_version}"
    
    story_patch = [
        {"op": "add", "path": "/fields/System.Title", "value": data.story.title},
        # No ADO a descrição costuma aceitar HTML, mas se injetarmos Markdown ele armazena em plain text (ou tenta renderizar limitadamente).
        {"op": "add", "path": "/fields/System.Description", "value": data.story.description_markdown.replace("\n", "<br>")}
    ]

    try:
        story_response = _create_work_item(story_url, ado_pat, story_patch)
        story_id = story_response["id"]
        story_url_ado = story_response["_links"]["html"]["href"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao criar User Story: {str(e)}")

    created_tasks = []

    # 2. Cria as Tasks filhas vinculadas à User Story
    task_url = f"{base_url}/{project}/_apis/wit/workitems/${data.work_item_type_task}?api-version={api_version}"

    for task in data.tasks:
        desc = task.description
        if task.layer:
            desc = f"<strong>Layer:</strong> {task.layer}<br><br>" + desc
        if task.estimated_risk:
            desc = f"<strong>Risk:</strong> {task.estimated_risk}<br><br>" + desc
        
        # Converte as quebras de linha pro ADO entender no campo rich text
        desc = desc.replace("\n", "<br>")

        task_patch = [
            {"op": "add", "path": "/fields/System.Title", "value": task.title},
            {"op": "add", "path": "/fields/System.Description", "value": desc},
            # Adiciona o link de parentesco para a story recém-criada
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": story_response["url"],
                    "attributes": {
                        "name": "Parent"
                    }
                }
            }
        ]

        try:
            task_resp = _create_work_item(task_url, ado_pat, task_patch)
            created_tasks.append({
                "id": task_resp["id"],
                "url": task_resp["_links"]["html"]["href"],
                "title": task.title
            })
        except Exception as e:
            # Se uma task falhar, não paramos o processo para não perder o que já foi criado, 
            # mas vamos adicionar aviso (ou poderia ser feito rollback).
            print(f"Atenção: Falha ao criar task '{task.title}': {str(e)}")
            created_tasks.append({
                "title": task.title,
                "error": str(e)
            })

    return {
        "message": "Operação finalizada com sucesso.",
        "story": {
            "id": story_id,
            "url": story_url_ado
        },
        "tasks_criadas": len([t for t in created_tasks if "id" in t]),
        "tasks": created_tasks
    }
