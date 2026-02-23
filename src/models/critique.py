class critique(BaseModel):
    field: str = Field(description="O campo da story que tem problema (ex: Critérios de Aceite)")
    issue: str = Field(description="Descrição clara do que está faltando ou está ambíguo")