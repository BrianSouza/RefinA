import asyncio
from agentes.agente_po import AgentePO

async def main():
    agentePO = AgentePO()
    story = """
    Quero evoluir a feature de consulta de CEP. Se durante a pesquisa da base de dados de CEPS, 
    o CEP não for encontrado, chamar o microserviço de CEP. Esse MS vai realizar uma chamada ao https dos correios e vai pesquisar 
    o CEP. Se o CEP for encontrado, o MS vai retornar o CEP para o sistema e o sistema vai salvar o CEP na base de dados de CEPS.
    """
    print("--- Iniciando chamada para o Agente (limite de 300s)...")
    try:
        resposta = await asyncio.wait_for(agentePO.run(story), timeout=300.0)
        
        print("\n--- RESPOSTA DA IA ---")
        print(resposta)
    except asyncio.TimeoutError:
        print("\n--- ERRO: A chamada demorou demais (Timeout de 300s) ---")
        print("Verifique sua conexão ou se a API Key tem saldo/créditos.")
    except Exception as e:
        print(f"\n--- OCORREU UM ERRO ---")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Detalhes: {e}")
    
asyncio.run(main())
    