from typing import List
from pydantic import BaseModel
from src.models.task import Task

class TechnicalRefinementOutput(BaseModel):
    ambiguities: List[str]
    technical_approach: str
    impacted_layers: List[str]
    risk_assessment: str
    tasks: List[Task]
    is_implementable: bool 
