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

class AgentBase(ABC):
    def __init__(self, caminhoPrompt: str, output_type=None):
        self.prompt = self.load_prompt(caminhoPrompt)
        self.output_type = output_type
        self.agent = self.create_agent()

    def load_prompt(self, caminhoPrompt: str):
        with open(caminhoPrompt,'r',encoding='utf-8') as arquivo:
            return arquivo.read()
    
    def create_agent(self) -> Agent:
        islocal = os.getenv("IS_LOCAL", "true").strip().lower() == "true"
        kwargs = {"system_prompt": self.prompt}
        if self.output_type is not None:
            kwargs["output_type"] = self.output_type
        if islocal:
            model_name = os.getenv("MODEL_LOCAL")
            base_url = os.getenv("OLLAMA_BASE_URL")
            api_key = os.getenv("API_KEY_LOCAL")
            provider = OllamaProvider(base_url=base_url, api_key=api_key)
            model = OpenAIChatModel(model_name=model_name, provider=provider)
            return Agent(model=model, **kwargs)
        else:
            model_name = os.getenv("MODEL")
            return Agent(model=model_name, **kwargs)
    
    @abstractmethod
    async def run(self, story: str) -> str:
        pass
    