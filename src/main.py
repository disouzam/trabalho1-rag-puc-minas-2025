"""
Módulo principal para o trabalho de uso de RAG para Engenharia de Software

Baseado no trabalho original do professor Samuel Cardoso com modificações
para o contexto de Engenharia de Software
"""

import logging
from typing import List
import faiss
from utils.custom_logging import logger_setup
from utils.llm_connection import get_llm_client
from utils.embeddings_processing import get_embedding, get_embeddings
from utils.indexing import search_index

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    logger_setup(logger, "trabalho-genai-rag-dickson.log")

    logger.info("===============================")
    logger.info("Início da execução")
    logger.info("")

    client = get_llm_client(logger)

    embeddings, chunks, index = get_embeddings(logger, client)

    print("Digite sua pergunta (ou 'sair' para terminar):")
    while True:
        query = input(">> ")
        if query.lower() == "sair":
            break
        answer = answer_query(query, index, chunks, client)
        print("\nResposta:\n", answer)

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")


def answer_query(
    query: str, index: faiss.IndexFlatL2, chunks: List[str], client, k: int = 5
) -> str:
    logger.info("Respondendo à pergunta do usuário.")
    query_embedding = get_embedding(logger, query, client)
    logger.debug("Query_embedding: %s", query_embedding)

    indices, distances = search_index(  # pylint: disable=unused-variable
        logger, index, query_embedding, k
    )

    logger.debug("Indices: %s", indices)

    relevant_chunks = [chunks[i] for i in indices]

    logger.warning("Chunks relevants\n")
    for contador, chunk in enumerate(relevant_chunks):
        logger.debug("Chunk relevante #%d: %s\n\n", contador, chunk)

    context = "\n\n".join(relevant_chunks)

    try:
        logger.debug("Contexto:\n%s", context)
        logger.debug("Query:\n%s", query)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um jogador profissional de xadrez"
                    + " e também cientista da computação.",
                },
                {"role": "system", "content": "Contexto:\n{context}\n\n"},
                {"role": "user", "content": f"Pergunta: {query}"},
            ],
            temperature=1,
        )
        answer = response.choices[0].message.content
        logger.debug("Resposta da LLM: %s", answer)
        return answer

    except IOError as ioerror:
        logger.error("Erro ao gerar a resposta: %s", ioerror)
        return "Desculpe, ocorreu um erro ao gerar a resposta."


if __name__ == "__main__":
    main()
