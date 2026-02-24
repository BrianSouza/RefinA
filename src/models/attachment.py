from typing import List, Optional
from pydantic import BaseModel, Field

class Attachment(BaseModel):
    file_name: str
    content: str  # Texto extraído do PDF/Doc ou URL do blob
    file_type: str # ex: "business_requirement", "technical_spec", "legacy_code"