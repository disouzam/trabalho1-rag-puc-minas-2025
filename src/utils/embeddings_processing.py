import os
import pickle
from typing import List
from utils.pdf_processing import extract_text_from_pdf
from utils.indexing import create_faiss_index
import faiss
from utils.chunk_processing import split_text_into_chunks


def get_embedding(
    logger, text: str, client, model: str = "text-embedding-3-small"
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
    logger, texts: List[str], client, model: str = "text-embedding-3-small"
) -> List[List[float]]:
    embeddings = []
    logger.info("Gerando embeddings para os chunks.")
    for i, text in enumerate(texts):
        embedding = get_embedding(logger, text, client, model)
        embeddings.append(embedding)
        if (i + 1) % 10 == 0 or (i + 1) == len(texts):
            logger.info("Processados %d / %d chunks.", i + 1, len(texts))
    return embeddings


def get_embeddings(logger, client):

    embeddings, chunks, index = load_embeddings(logger)
    if len(embeddings) == 0:
        logger.info(
            "Embeddings não encontrados. Processando PDF e criando embeddings..."
        )
        # pdf_path = "../pdfs/manual_de_normalizacao_abnt.pdf"
        # pdf_path = "../pdfs/Paper_PESSOAS_DIGITAL_Silvio_Meira.pdf"
        pdf_path = "../pdfs/knightstour-SBPO.pdf"

        logger.debug("Arquivo sendo processado: %s", pdf_path)

        text = extract_text_from_pdf(logger, pdf_path)
        logger.debug("Comprimento do texto extraído: %d", len(text))

        chunks = split_text_into_chunks(logger, text)
        logger.debug("Número de chunks gerados: %d", len(chunks))

        embeddings = create_embeddings(logger, chunks, client)
        logger.debug(
            "Tamanho da lista de embeddings gerada a partir dos chunks: %d",
            len(embeddings),
        )

        index: faiss.IndexFlatL2 = create_faiss_index(logger, embeddings)
        save_embeddings(logger, embeddings, chunks, index)
        logger.info("Embeddings e índice salvos.")
    else:
        logger.info("Embeddings carregados dos arquivos.")

    return embeddings, chunks, index


def save_embeddings(
    logger,
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
    logger,
    embeddings_file: str = "embeddings.pkl",
    chunks_file: str = "chunks.pkl",
    index_file: str = "faiss.index",
) -> tuple[List[List[float]], List[str], faiss.IndexFlatL2]:
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
        index: faiss.IndexFlatL2 = faiss.read_index(index_file)
        return embeddings, chunks, index

    logger.warning("Arquivos de embeddings não encontrados.")
    embeddings: List[List[float]] = []
    chunks: List[str] = []
    index = faiss.IndexFlatL2()
    return embeddings, chunks, index
