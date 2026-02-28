from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.attachment import Attachment

class input_story(BaseModel):
    user_prompt: str = Field(description="A descrição inicial ou comando do usuário")
    project_context: str = Field(description="Contexto do sistema (ex: Microserviço de Pix, Legado C#)")
    documents: List[Attachment] = Field(default=[], description="Documentos de apoio anexados")
    iteration_history: Optional[List[str]] = Field(default=[], description="Logs de ajustes anteriores para manter memória")