import os   
import asyncio
import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# Configura o logfire para mostrar o que acontece "por baixo do capô"
logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record='all'))
logfire.instrument_pydantic_ai()

def carregar_prompt(caminho_arquivo):
    with open(caminho_arquivo,'r',encoding='utf-8') as arquivo:
        return arquivo.read()

def criar_agente():
    print("--- Carregando Prompt do arquivo...")
    prompt_conteudo = carregar_prompt("prompts/refina_prompt.txt")
    
    modelo = os.getenv("MODEL")
    print(f"--- Usando o modelo: {modelo}")
    
    return Agent(
        model=modelo,
        system_prompt=prompt_conteudo,
    )

async def main():
    story = """
    Quero evoluir a feature de consulta de CEP. Se durante a pesquisa da base de dados de CEPS, 
    o CEP não for encontrado, chamar o microserviço de CEP. Esse MS vai realizar uma chamada ao https dos correios e vai pesquisar 
    o CEP. Se o CEP for encontrado, o MS vai retornar o CEP para o sistema e o sistema vai salvar o CEP na base de dados de CEPS.
    """
    print("--- Iniciando chamada para o Agente (limite de 60s)...")
    try:
        agente = criar_agente()
        # Adicionamos um timeout de 60 segundos para não ficar travado para sempre
        resposta = await asyncio.wait_for(agente.run(story), timeout=60.0)
        
        print("\n--- RESPOSTA DA IA ---")
        print(resposta.output)
    except asyncio.TimeoutError:
        print("\n--- ERRO: A chamada demorou demais (Timeout de 60s) ---")
        print("Verifique sua conexão ou se a API Key tem saldo/créditos.")
    except Exception as e:
        print(f"\n--- OCORREU UM ERRO ---")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Detalhes: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    