import os   
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
#Carrega as variaveis de ambiente, para utilizar as chaves utilize o os.getenv.
load_dotenv()

def criar_agente():
    return Agent(
        model=os.getenv("MODEL"),
        system_prompt="Você é um agente de IA especializado em análise de dados financeiros.",
    )

async def main():
    agente = criar_agente()
    resposta = await agente.run("Olá, como vai você?")
    print(resposta.output)

if __name__ == "__main__":
    asyncio.run(main())
    