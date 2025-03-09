"""Proof of concept to remove comments, empty lines and docstrings"""

import os
import sys
import logging
import libcst as cst
from src.utils.custom_logging import logger_setup
from src.utils.concrete_syntax_tree_parsing import (
    TypingCollector,
    RemoveDocStringTransformer,
)

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main(file_path):

    logger.info("Processing file %s", file_path)
    try:
        with open(file=file_path, mode="r", encoding="utf-8") as f:  # filename input
            file_content = f.read()
    except IOError:
        logger.error("Failed to parse file %s", file_path)
        return

    source_tree = cst.parse_module(source=file_content)

    # logger.warning(source_tree)

    visitor = TypingCollector()
    transformer = RemoveDocStringTransformer(visitor)
    modified_tree = source_tree.visit(transformer)

    print(modified_tree.code)
    file_reconstructed = modified_tree.code

    with open(file_path, "w", encoding="utf-8") as f:  # filename output
        f.write(file_reconstructed)


if __name__ == "__main__":
    logger_setup(logger, "pocs/remove_doc_strings_python_file.log")

    logger.info("===============================")
    logger.info("Início da execução")
    logger.info("")

    folder_path = sys.argv[1]
    abs_path = os.path.abspath(folder_path)

    for dirpath, dirnames, filenames in os.walk(abs_path):
        print(dirpath)
        print(dirnames)
        print(filenames)

        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename)
                main(fullpath)

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")
