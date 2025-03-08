import os
import libcst as cst
import sys
import logging
from typing import List, Tuple, Dict, Optional
from src.utils.custom_logging import logger_setup


class TypingCollector(cst.CSTVisitor):
    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[Tuple[str, ...]] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[cst.Parameters, Optional[cst.Annotation]],  # value: (params, returns)
        ] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        self.annotations[tuple(self.stack)] = (node.params, node.returns)
        return False  # pyi files don't support inner functions, return False to stop the traversal.

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.stack.pop()


class TypingTransformer(cst.CSTTransformer):
    def __init__(self, annotations):
        # stack for storing the canonical name of the current function
        self.stack: List[Tuple[str, ...]] = []
        # store the annotations
        self.annotations: Dict[
            Tuple[str, ...],  # key: tuple of canonical class/function name
            Tuple[cst.Parameters, Optional[cst.Annotation]],  # value: (params, returns)
        ] = annotations

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        self.stack.pop()
        return updated_node

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.stack.append(node.name.value)
        return False  # pyi files don't support inner functions, return False to stop the traversal.

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        key = tuple(self.stack)
        self.stack.pop()
        if key in self.annotations:
            annotations = self.annotations[key]
            return updated_node.with_changes(
                params=annotations[0], returns=annotations[1]
            )
        return updated_node


# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main(file_path):

    logger.info("Processing file %s", file_path)
    try:
        with open(file=file_path, mode="r", encoding="utf-8") as f:  # filename input
            file_content = f.read()
    except:
        logger.error("Failed to parse file %s", file_path)
        return

    source_tree = cst.parse_module(source=file_content)

    visitor = TypingCollector()
    transformer = TypingTransformer(visitor.annotations)
    modified_tree = source_tree.visit(transformer)

    print(modified_tree.code)
    file_reconstructed = modified_tree.code

    with open(file_path, "w", encoding="utf-8") as f:  # filename output
        f.write(file_reconstructed)


if __name__ == "__main__":
    logger_setup(logger, "pocs/reconstruct_python_file.log")

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
