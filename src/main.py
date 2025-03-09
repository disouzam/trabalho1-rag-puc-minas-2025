"""
Módulo principal para o trabalho de uso de RAG para Engenharia de Software

Baseado no trabalho original do professor Samuel Cardoso com modificações
para o contexto de Engenharia de Software
"""

import os
import re
import logging
import pickle
from typing import List
import numpy as np
import faiss
import PyPDF2
from utils.custom_logging import logger_setup
from utils.llm_connection import get_llm_client

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


def extract_text_from_pdf(pdf_path: str) -> str:
    logger.info("Extraindo texto do PDF: %s", pdf_path)
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except IOError as ioerror:
        logger.error("Erro ao ler o arquivo PDF: %s", ioerror)
    return text


def split_text_into_chunks(text: str, max_chunk_size: int = 5000) -> List[str]:
    logger.info("Dividindo o texto em chunks.")
    sentences = re.split(r"(?<=[.?!])\s+", text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    logger.info("Total de chunks criados: %d", len(chunks))
    return chunks


def get_embedding(
    text: str, client, model: str = "text-embedding-3-small"
) -> List[float]:
    text = text.replace("\n", " ")
    try:
        response = client.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        return embedding
    except IOError as ioerror:
        logger.error("Erro ao obter embedding para o texto: %s", ioerror)
        return []


def create_embeddings(
    texts: List[str], client, model: str = "text-embedding-3-small"
) -> List[List[float]]:
    embeddings = []
    logger.info("Gerando embeddings para os chunks.")
    for i, text in enumerate(texts):
        embedding = get_embedding(text, client, model)
        embeddings.append(embedding)
        if (i + 1) % 10 == 0 or (i + 1) == len(texts):
            logger.info("Processados %d / %d chunks.", i + 1, len(texts))
    return embeddings


def get_embeddings(logger, client):

    embeddings, chunks, index = load_embeddings()
    if embeddings is None:
        logger.info(
            "Embeddings não encontrados. Processando PDF e criando embeddings..."
        )
        # pdf_path = "../pdfs/manual_de_normalizacao_abnt.pdf"
        # pdf_path = "../pdfs/Paper_PESSOAS_DIGITAL_Silvio_Meira.pdf"
        pdf_path = "../pdfs/knightstour-SBPO.pdf"

        logger.debug("Arquivo sendo processado: %s", pdf_path)

        text = extract_text_from_pdf(pdf_path)
        logger.debug("Comprimento do texto extraído: %d", len(text))

        chunks = split_text_into_chunks(text)
        logger.debug("Número de chunks gerados: %d", len(chunks))

        embeddings = create_embeddings(chunks, client)
        logger.debug(
            "Tamanho da lista de embeddings gerada a partir dos chunks: %d",
            len(embeddings),
        )

        index: faiss.IndexFlatL2 = create_faiss_index(embeddings)
        save_embeddings(embeddings, chunks, index)
        logger.info("Embeddings e índice salvos.")
    else:
        logger.info("Embeddings carregados dos arquivos.")

    return embeddings, chunks, index


def create_faiss_index(embeddings: List[List[float]]) -> faiss.IndexFlatL2:
    logger.info("Criando índice FAISS.")
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index


def save_embeddings(
    embeddings: List[List[float]],
    chunks: List[str],
    index: faiss.IndexFlatL2,
    embeddings_file: str = "embeddings.pkl",
    chunks_file: str = "chunks.pkl",
    index_file: str = "faiss.index",
):
    logger.info("Salvando embeddings, chunks e índice no disco.")
    with open(embeddings_file, "wb") as f:
        pickle.dump(embeddings, f)
    with open(chunks_file, "wb") as f:
        pickle.dump(chunks, f)
    faiss.write_index(index, index_file)


def load_embeddings(
    embeddings_file: str = "embeddings.pkl",
    chunks_file: str = "chunks.pkl",
    index_file: str = "faiss.index",
):
    if (
        os.path.exists(embeddings_file)
        and os.path.exists(chunks_file)
        and os.path.exists(index_file)
    ):
        logger.info("Carregando embeddings, chunks e índice do disco.")
        with open(embeddings_file, "rb") as f:
            embeddings = pickle.load(f)
        with open(chunks_file, "rb") as f:
            chunks = pickle.load(f)
        index = faiss.read_index(index_file)
        return embeddings, chunks, index

    logger.warning("Arquivos de embeddings não encontrados.")
    return None, None, None


def search_index(index: faiss.IndexFlatL2, query_embedding: List[float], k: int = 5):
    logger.info("Pesquisando no índice FAISS por embeddings similares.")
    query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]


def answer_query(
    query: str, index: faiss.IndexFlatL2, chunks: List[str], client, k: int = 5
) -> str:
    logger.info("Respondendo à pergunta do usuário.")
    query_embedding = get_embedding(query, client)
    logger.debug("Query_embedding: %s", query_embedding)

    indices, distances = search_index(  # pylint: disable=unused-variable
        index, query_embedding, k
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
