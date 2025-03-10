"""
Módulo principal para o trabalho de uso de RAG para Engenharia de Software

Baseado no trabalho original do professor Samuel Cardoso com modificações
para o contexto de Engenharia de Software
"""

import logging
import os
from typing import List, Tuple
from dotenv import load_dotenv
from enum import Enum
import libcst as cst
from utils.concrete_syntax_tree_parsing import (
    InsertDocStringTransformer,
    InsertDocStringVisitor,
    get_undocumented_functions,
)
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


class Modos(Enum):
    SOMENTE_SUGESTAO = 0
    ALTERACAO_CODIGO = 1


modo = Modos.ALTERACAO_CODIGO


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

    undocumented_functions: dict[str, Tuple[List[str], List[str]]] = {}

    for file_name in file_names:
        with open(file_name, mode="r", encoding="utf-8") as code_file:
            file_content = code_file.read()

        undocumented_function_and_names = get_undocumented_functions(
            logger, code_content=file_content, file_name=file_name
        )

        undocumented_functions[file_name] = undocumented_function_and_names

    system_prompt = (
        "Você é um assistente de geração de documentação de códigos em Python."
    )

    command = ""
    for item in undocumented_functions.items():

        file_name = item[0]
        functions_to_rewrite = []
        docstrings = []
        functions_and_docstrings = {}
        undoc_functions = item[1][1]

        for pos_function, function in enumerate(undoc_functions):
            query = (
                f"Gere a docstring para essa função, no idioma inglês: \n {function}"
            )

            logger.info(
                "Essa é a função que se deseja gerar uma docstring: \n%s", function
            )

            # command = input("Pressione Enter para enviar pergunta ao ChatGPT...\n")

            answer = answer_query(
                logger=logger,
                query=query,
                index=index,
                chunks=chunks,
                system_prompt=system_prompt,
                client=client,
            )
            print("\n\nResposta:\n", answer)

            if modo == Modos.ALTERACAO_CODIGO:
                # Extrai nome
                function_name = item[1][0][pos_function]

                docstring = answer.split("\n")
                docstring = docstring[2:-1]
                docstring = "\n".join(docstring)
                docstring = docstring.strip()

                #  Remove leading double quotes
                while docstring[0] == '"':
                    docstring = docstring[1:]

                #  Remove leading double quotes
                while docstring[-1] == '"':
                    docstring = docstring[:-1]

                docstring = '"""' + docstring + '"""'
                # docstring = "'" + docstring + "'"

                functions_and_docstrings[function_name] = docstring

            # command = input("Pressione Enter para continuar ou Digite X pra sair.\n")
            # if command.lower() == "x":
            #     break

        # InsertDocStringVisitor, InsertDocStringTransformer
        visitor = InsertDocStringVisitor()
        transformer = InsertDocStringTransformer(
            visitor=visitor,
            functions_and_docstrings=functions_and_docstrings,
        )
        with open(file_name, mode="r", encoding="utf-8") as code_file:
            file_content = code_file.read()
        source_tree = cst.parse_module(source=file_content)
        modified_tree = source_tree.visit(transformer)

        file_reconstructed = modified_tree.code

        with open(file_name, "w", encoding="utf-8") as f:  # filename output
            f.write(file_reconstructed)

        if command.lower() == "x":
            break

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")


if __name__ == "__main__":
    main()
