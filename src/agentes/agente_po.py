from agentes.agente_base import AgenteBase

class AgentePO(AgenteBase):
    def __init__(self):
        super().__init__("src/prompts/refina_storyprompt.txt")
    
    async def run(self, story: str) -> str:
        resposta = await self.agente.run(story)
        return resposta.output