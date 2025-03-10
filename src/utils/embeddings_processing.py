import os
import pickle
from typing import List
import faiss
from dotenv import load_dotenv
from utils.pdf_processing import extract_text_from_pdf
from utils.indexing import create_faiss_index
from utils.chunk_processing import split_text_into_chunks, split_code_into_chunks
from utils.repository_processing import extract_source_code_from_repository


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
        logger.info("Tamanho do texto para gerar embedding %d", len(text))
        embedding = get_embedding(logger, text, client, model)
        embeddings.append(embedding)
        if (i + 1) % 10 == 0 or (i + 1) == len(texts):
            logger.info("Processados %d / %d chunks.", i + 1, len(texts))
    return embeddings


def get_embeddings_from_PDF_files(logger, client):

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


def get_embeddings_from_code_bases(logger, client):

    embeddings_file = "embeddings_code.pkl"
    chunks_file = "chunks_code.pkl"
    index_file = "faiss_code.index"

    embeddings, chunks, index = load_embeddings(
        logger=logger,
        embeddings_file=embeddings_file,
        chunks_file=chunks_file,
        index_file=index_file,
    )
    if len(embeddings) == 0:
        logger.info(
            "Embeddings não encontrados. Processando repositórios de código e criando os embeddings..."
        )

        load_dotenv()
        code_repository_path = os.getenv("REPOSITORY_1_PATH")

        logger.debug("Repositório sendo processado %s", code_repository_path)

        code_file_contents, file_names = extract_source_code_from_repository(
            logger, code_repository_path
        )

        logger.debug(
            "Número de arquivos-fonte a serem processados: %d", len(code_file_contents)
        )

        for code_file_position, code_file_content in enumerate(code_file_contents):
            file_name = file_names[code_file_position]
            current_file_chunks = split_code_into_chunks(
                logger=logger, code_content=code_file_content, file_name=file_name
            )
            chunks = chunks + current_file_chunks

        logger.debug("Número de chunks gerados: %d", len(chunks))

        embeddings = create_embeddings(logger, chunks, client)
        logger.debug(
            "Tamanho da lista de embeddings gerada a partir dos chunks: %d",
            len(embeddings),
        )

        index: faiss.IndexFlatL2 = create_faiss_index(logger, embeddings)

        save_embeddings(
            logger=logger,
            embeddings=embeddings,
            chunks=chunks,
            index=index,
            embeddings_file=embeddings_file,
            chunks_file=chunks_file,
            index_file=index_file,
        )
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
