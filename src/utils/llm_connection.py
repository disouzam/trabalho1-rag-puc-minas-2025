import os
from dotenv import load_dotenv
from openai import OpenAI


def get_llm_client(logger):
    # Carregar variáveis de ambiente
    api_key = get_api_key(logger)

    # Criar o cliente OpenAI
    client = OpenAI(api_key=api_key, max_retries=5)

    return client


def get_api_key(logger):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "Chave da API da OpenAI não encontrada. Defina OPENAI_API_KEY no seu arquivo .env"
        )
        return None
    return api_key
