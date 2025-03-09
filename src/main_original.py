"""
Módulo principal para o trabalho de uso de RAG para Engenharia de Software

Aplicação original modificada ligeiramente mas que executa as funções originais
de uma RAG focada em processamento de documentos textuais

Baseada integralmente no trabalho do professor Samuel Cardoso.
Modificações feitas por Dickson Souza podem ser conferidas no histórico de commits do repositório
"""

import logging
from utils.custom_logging import logger_setup
from utils.llm_connection import get_llm_client
from utils.embeddings_processing import get_embeddings_from_PDF_files
from utils.query_processing import answer_query

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    logger_setup(logger, "genai-rag-original.log")

    logger.info("===============================")
    logger.info("Início da execução")
    logger.info("")

    client = get_llm_client(logger)

    embeddings, chunks, index = get_embeddings_from_PDF_files(logger, client)

    print("Digite sua pergunta (ou 'sair' para terminar):")
    while True:
        query = input(">> ")
        if query.lower() == "sair":
            break
        answer = answer_query(logger, query, index, chunks, client)
        print("\nResposta:\n", answer)

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")


if __name__ == "__main__":
    main()
