from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOllama
import os
import requests

class RecipeAgent:
    def __init__(self):
        base_url = os.getenv("OLLAMA_BASE_URL")
        model = os.getenv("OLLAMA_MODEL")

        self.llm = ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL"),  # Corrigido: strings entre aspas
            model=os.getenv("OLLAMA_MODEL"),  # Corrigido: strings entre aspas
        )

        try:
            response = requests.post(f"{base_url}/api/clear", json={"model": model})
            print("🧹 Memória do Ollama limpa:", response.status_code)
        except Exception as e:
            print("Erro limpando memória do Ollama:", e)

        # Create the recipe agent
        self.recipe_agent = Agent(
            role="Especialista em Receitas",
            goal="Gerar receitas deliciosas e práticas baseadas nos ingredientes fornecidos",
            backstory="""Você é um chef especialista e criador de receitas com anos de experiência
            na criação de pratos deliciosos com diversos ingredientes. Você sabe como combinar
            ingredientes de forma criativa e sugerir métodos práticos de cozimento.""",
            llm=self.llm,
            verbose=True,
        )

    async def process_message(self, message: str) -> str:
        """Process the incoming message and generate recipe suggestions."""
        task = Task(
            description=f"""*Ingredientes Recebidos:* {message}

            *Por favor, forneça:*
            1. *Uma sugestão de receita estritamente com os ingredientes recebidos*

            *Para cada receita, inclua:*
            - *Lista de Ingredientes Necessários*
            - *Instruções Passo a Passo*
            - *Tempo Estimado de Preparo*
            - *Nível de Dificuldade*

            *Formate a resposta de forma clara e fácil de ler, utilizando negrito para destacar informações importantes. Limite a resposta a 1000 caracteres para garantir uma boa visualização no WhatsApp.*""",
            expected_output="Uma lista de 2-3 receitas completas com título, ingredientes, passos, tempo e dificuldade.",
            agent=self.recipe_agent,
        )

        crew = Crew(agents=[self.recipe_agent], tasks=[task], verbose=True)

        result = await crew.kickoff_async()
        return str(result)
