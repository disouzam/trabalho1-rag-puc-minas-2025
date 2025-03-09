import re
import libcst as cst
from typing import List

from utils.concrete_syntax_tree_parsing import (
    FunctionWithDocsStrings,
    RemoveFunctionsWithoutDocStrings,
)


def split_text_into_chunks(logger, text: str, max_chunk_size: int = 5000) -> List[str]:
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


def split_code_into_chunks(logger, text: str, max_chunk_size: int = 5000) -> List[str]:
    logger.info("Dividindo o texto em chunks.")

    source_tree = cst.parse_module(source=text)
    logger.warning(source_tree.code)

    visitor = FunctionWithDocsStrings()
    transformer = RemoveFunctionsWithoutDocStrings(visitor)
    modified_tree = source_tree.visit(transformer)

    logger.warning(modified_tree.code)

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
