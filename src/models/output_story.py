from typing import List
from pydantic import BaseModel, Field
from src.models.critique import critique


class output_story(BaseModel):
    story_markdown: str = Field(description="A User Story formatada em Markdown")
    is_satisfactory: bool = Field(description="Define se a story está pronta para o refinamento técnico")
    critiques: List[critique] = Field(default=[], description="Lista de problemas encontrados, caso não esteja satisfatória")
    uncertainty_score: float = Field(description="Score de 0 a 1 de quanto o agente está seguro sobre o contexto fornecido")