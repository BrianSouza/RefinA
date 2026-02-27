from pydantic import BaseModel, Field
class Task(BaseModel):
    title: str
    prompt_for_ai: str = Field(description="A instrução técnica detalhada para o assistente de codificação")
    definition_of_done: str
    layer: str
    estimated_risk: str