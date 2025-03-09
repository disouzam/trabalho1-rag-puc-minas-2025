from typing import List
import faiss
from utils.embeddings_processing import get_embedding
from utils.indexing import search_index


def answer_query(
    logger, query: str, index: faiss.IndexFlatL2, chunks: List[str], client, k: int = 5
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
