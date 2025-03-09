import re
from typing import List


def split_text_into_chunks(logger, text: str, max_chunk_size: int = 5000) -> List[str]:
    logger.info("Dividindo o texto em chunks.")

    # Aqui possivelmente faça sentido uma versão dedicada para extrair funções
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
