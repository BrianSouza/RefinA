from abc import ABC, abstractmethod
import os   
import asyncio
import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.openai import OpenAIChatModel


load_dotenv()
logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record='all'))
logfire.instrument_pydantic_ai()

class AgenteBase(ABC):
    def __init__(self,caminhoPrompt: str):
        self.prompt = self.carregar_prompt(caminhoPrompt)
        self.agente = self.criar_agente()

    def carregar_prompt(self, caminhoPrompt: str):
        with open(caminhoPrompt,'r',encoding='utf-8') as arquivo:
            return arquivo.read()
    
    def criar_agente(self) -> Agent:
        islocal = os.getenv("IS_LOCAL", "true").strip().lower() == "true"
        if islocal:
            modelo = os.getenv("MODEL_LOCAL")
            base_url = os.getenv("OLLAMA_BASE_URL")
            api_key = os.getenv("API_KEY_LOCAL")
            provider = OllamaProvider(base_url=base_url, api_key=api_key)
            model = OpenAIChatModel(model_name=modelo, provider=provider)
            return Agent(
                model=model,
                system_prompt=self.prompt,
            )
        else:
            modelo = os.getenv("MODEL")
            return Agent(
                model=modelo,
                system_prompt=self.prompt,
            )
    
    @abstractmethod
    async def run(self, story: str) -> str:
        pass
    