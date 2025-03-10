"""
Módulo principal para o trabalho de uso de RAG para Engenharia de Software

Baseado no trabalho original do professor Samuel Cardoso com modificações
para o contexto de Engenharia de Software
"""

import logging
import os
from typing import List
from dotenv import load_dotenv
from utils.concrete_syntax_tree_parsing import get_undocumented_functions
from utils.custom_logging import logger_setup
from utils.llm_connection import get_llm_client
from utils.embeddings_processing import (
    get_embeddings_from_code_bases,
)
from utils.query_processing import answer_query
from utils.repository_processing import get_all_python_files_from_repository

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    logger_setup(logger, "trabalho-genai-rag-dickson.log")

    logger.info("===============================")
    logger.info("Início da execução")
    logger.info("")

    client = get_llm_client(logger)

    embeddings, chunks, index = get_embeddings_from_code_bases(logger, client)

    load_dotenv()
    code_repository_path = os.getenv("REPOSITORY_1_PATH")

    logger.debug(
        "Repositório sendo processado para obtenção de funções sem documentação: %s",
        code_repository_path,
    )

    file_names = get_all_python_files_from_repository(logger, code_repository_path)

    undocumented_functions: dict[str, List[str]] = {}

    for file_name in file_names:
        with open(file_name, mode="r", encoding="utf-8") as code_file:
            file_content = code_file.read()

        undocumented = get_undocumented_functions(
            logger, code_content=file_content, file_name=file_name
        )

        undocumented_functions[file_name] = undocumented

    system_prompt = (
        "Você é um assistente de geração de documentação de códigos em Python."
    )

    command = ""
    for item in undocumented_functions.items():

        file_name = item[0]
        undoc_functions = item[1]

        for function in undoc_functions:
            query = (
                f"Gere a docstring para essa função, no idioma inglês: \n {function}"
            )

            logger.info(
                "Essa é a função que se deseja gerar uma docstring: \n%s", function
            )

            command = input("Pressione Enter para enviar pergunta ao ChatGPT...\n")

            answer = answer_query(
                logger=logger,
                query=query,
                index=index,
                chunks=chunks,
                system_prompt=system_prompt,
                client=client,
            )
            print("\n\nResposta:\n", answer)

            command = input("Pressione Enter para continuar ou Digite X pra sair.\n")
            if command.lower() == "x":
                break

        if command.lower() == "x":
            break

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")


if __name__ == "__main__":
    main()
