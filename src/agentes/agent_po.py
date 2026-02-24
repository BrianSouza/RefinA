import time
import logfire
from agentes.agent_base import AgentBase
from pydantic_graph import End
from models.input_story import input_story
from models.output_story import output_story

class AgentPO(AgentBase):
    def __init__(self):
        super().__init__("src/prompts/refina_storyprompt.txt", output_type=output_story)

    async def run(self, input_story: input_story) -> output_story:
        inicio_total = time.perf_counter()
        logfire.info("🚀 AgentePO iniciando refinamento de story...")
        
        prompt_input = (
            f"Contexto do Projeto: {input_story.project_context}\n"
            f"Input do Usuário: {input_story.user_prompt}\n"
            f"Documentos: {input_story.documents}"
        )
        async with self.agent.iter(prompt_input) as agent_run:
            node_count = 0
            async for node in agent_run:
                inicio_no = time.perf_counter()
                node_count += 1
                node_type = type(node).__name__

                if node_type == "ModelRequestNode":
                    logfire.info(
                        "📤 [{count}] Enviando requisição ao LLM: {node_type}",
                        count=node_count,
                        node_type=node_type,
                    )

                elif node_type == "CallToolsNode":
                    logfire.info(
                        "🔧 [{count}] LLM retornou - processando tools/resposta: {node_type}",
                        count=node_count,
                        node_type=node_type,
                    )

                elif isinstance(node, End):
                    logfire.info(
                        "✅ [{count}] Agente concluiu após {total} nós.",
                        count=node_count,
                        total=node_count,
                    )

                else:
                    logfire.info(
                        "❓ [{count}] Nó: {node_type}",
                        count=node_count,
                        node_type=node_type,
                    )

                duracao_no = time.perf_counter() - inicio_no
                logfire.info(
                    "⏱️  Nó {node_type} executou em {duracao:.3f}s",
                    node_type=node_type,
                    duracao=duracao_no,
                )

        resultado = agent_run.result.output
        duracao_total = time.perf_counter() - inicio_total
        logfire.info(
            "📝 Story processada em {duracao:.2f}s. Status Satisfatório: {status}",
            duracao=duracao_total,
            status=resultado.is_satisfactory,
        )
        return resultado