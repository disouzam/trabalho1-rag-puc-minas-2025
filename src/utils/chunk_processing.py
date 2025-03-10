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


def split_code_into_chunks(
    logger, code_content: str, file_name: str, max_chunk_size: int = 5000
) -> List[str]:
    logger.info("Dividindo o código-fonte do arquivo %s em chunks.", file_name)

    source_tree = cst.parse_module(source=code_content)

    visitor = FunctionWithDocsStrings()
    transformer = RemoveFunctionsWithoutDocStrings(visitor)
    modified_tree = source_tree.visit(transformer)

    function_chunks = transformer.function_chunks

    chunks = []
    current_chunk = ""
    for function_chunk in function_chunks:
        if len(function_chunk) <= max_chunk_size:
            chunks.append(function_chunk)
        else:
            original_chunk_size = len(function_chunk)
            splitted_function = function_chunk.split("\n")

            partial_chunk = ""
            for splitted_line in splitted_function:
                if len(partial_chunk) + len(splitted_line) + 1 <= max_chunk_size:
                    partial_chunk += "\n" + splitted_line
                else:
                    if len(partial_chunk) > 0:
                        chunks.append(partial_chunk)
                    partial_chunk = splitted_line

            if len(partial_chunk) > 0:
                chunks.append(partial_chunk)

    logger.info("Total de chunks criados: %d", len(chunks))
    return chunks
