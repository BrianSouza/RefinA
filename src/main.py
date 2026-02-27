import asyncio
from agentes.agent_po import AgentPO
from models.input_story import input_story

async def main():
    agentPO = AgentPO()
    story = """
    Quero evoluir a feature de consulta de CEP. Se durante a pesquisa da base de dados de CEPS, 
    o CEP não for encontrado, chamar o microserviço de CEP. Esse MS vai realizar uma chamada ao https dos correios e vai pesquisar 
    o CEP. Se o CEP for encontrado, o MS vai retornar o CEP para o sistema e o sistema vai salvar o CEP na base de dados de CEPS.
    """
    print("--- Iniciando chamada para o Agente (limite de 300s)...")
    try:
        input_data = input_story(
            user_prompt=story,
            project_context="Microserviço de Logística - Arquitetura de mensageria e SQL Server.",
            documents=[] 
        )
        print("\n--- [1/2] Executando Agente PO (Refinamento da Story) ---")
        resposta = await asyncio.wait_for(agentPO.run(input_data), timeout=300.0)
        
        print("\n--- RESPOSTA DO AGENTE PO ---")
        print(resposta)
        
        #TODO: Trecho de código forçado para teste
        resposta.is_satisfactory = True
        
        if resposta.is_satisfactory:
            from agentes.agent_dev import AgentDev
            agentDev = AgentDev()
            
            print("\n--- [2/2] Executando Agente Dev (Criação das Tasks) ---")
            tasks_output = await asyncio.wait_for(agentDev.run(input_data, resposta), timeout=300.0)
            
            print("\n--- RESPOSTA DO AGENTE DEV (TASKS TÉCNICAS) ---")
            print(tasks_output)
        else:
            print("\n--- ATENÇÃO: A User Story não está satisfatória. ---")
            print("O Agente PO gerou críticas/dúvidas que precisam ser resolvidas antes de criar as tasks técnicas.")
            if resposta.critiques:
                for critique in resposta.critiques:
                    print(f"- {critique}")
                    
    except asyncio.TimeoutError:
        print("\n--- ERRO: A chamada demorou demais (Timeout de 300s) ---")
        print("Verifique sua conexão ou se a API Key tem saldo/créditos.")
    except Exception as e:
        print(f"\n--- OCORREU UM ERRO ---")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Detalhes: {e}")
    
asyncio.run(main())
    