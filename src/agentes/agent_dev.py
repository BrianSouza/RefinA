import os
import time
import logfire
from agentes.agent_base import AgentBase
from pydantic_graph import End
from models.input_story import input_story
from models.output_story import output_story
from models.TechnicalRefinementOutput import TechnicalRefinementOutput

class AgentDev(AgentBase):
    def __init__(self):
        super().__init__("src/prompts/refina_taskprompt.txt", output_type=TechnicalRefinementOutput)


    async def run(self, original_input: input_story, story_refined: output_story) -> TechnicalRefinementOutput:
        inicio_total = time.perf_counter()
        logfire.info("🚀 AgenteDev iniciando refinamento...")
        
        # Formatando anexos se existirem
        docs_text = "\n".join([f"- {doc.name}: {doc.content}" for doc in original_input.documents]) if original_input.documents else "Nenhum documento anexado."

        prompt_input = (
            f"Você recebeu uma User Story refinada pelo Product Owner e precisa quebrá-la em tarefas técnicas.\n\n"
            f"### 1. CONTEXTO DO PROJETO E USUÁRIO\n"
            f"- **Contexto do Projeto:** {original_input.project_context}\n"
            f"- **Pedido Original do Usuário:** {original_input.user_prompt}\n\n"
            f"### 2. USER STORY APROVADA\n"
            f"{story_refined.story_markdown}\n\n"
            f"### 3. DOCUMENTAÇÃO TÉCNICA DE APOIO\n"
            f"{docs_text}"
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
        uso = agent_run.usage()
        duracao_total = time.perf_counter() - inicio_total
        
        islocal = os.getenv("IS_LOCAL", "true").strip().lower() == "true"
        model_name = ""
        if islocal:
            model_name = os.getenv("MODEL_LOCAL")
        else:
            model_name = os.getenv("MODEL")

        logfire.info(
            "📝 Tasks processadas em {duracao:.2f}s. Status Implementável: {status}",
            duracao=duracao_total,
            status=resultado.is_implementable,
            gen_ai_usage_input_tokens=uso.request_tokens,
            gen_ai_usage_output_tokens=uso.response_tokens,
            gen_ai_system=model_name,
        )

        
        return resultado