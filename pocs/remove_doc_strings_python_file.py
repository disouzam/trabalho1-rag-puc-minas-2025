"""Proof of concept to remove comments, empty lines and docstrings"""

import os
import sys
import logging
import libcst as cst
from src.utils.custom_logging import logger_setup


class TypingCollector(cst.CSTVisitor):
    def __init__(self):
        pass


class RemoveDocStringTransformer(cst.CSTTransformer):
    def __init__(self, visitor):
        self.visitor = visitor
        self.docstring: str | None = None

    def leave_Comment(self, original_node, updated_node):
        """Remove comments"""
        updated_node = cst.RemoveFromParent()
        return super().leave_Comment(original_node, updated_node)

    def leave_EmptyLine_comment(self, node):
        """Remove comments"""
        node = cst.RemoveFromParent()
        return super().leave_EmptyLine_comment(node)

    def leave_Element(self, original_node, updated_node):
        if isinstance(original_node, cst.EmptyLine):
            print(original_node)
        return super().leave_Element(original_node, updated_node)

    def visit_FunctionDef(self, node):
        docstring = node.get_docstring()
        if docstring is not None:
            self.docstring = docstring

    def visit_Module(self, node):
        docstring = node.get_docstring()
        if docstring is not None:
            self.docstring = docstring

    def leave_EmptyLine(self, original_node, updated_node):
        """Remove empty lines"""
        updated_node = cst.RemoveFromParent()
        return super().leave_EmptyLine(original_node, updated_node)

    def leave_SimpleString(self, original_node, updated_node):

        if original_node.value == f'"""{self.docstring}"""':
            new_node = cst.Comment("# It was a docstring before")
        else:
            new_node = updated_node

        return super().leave_SimpleString(original_node, new_node)

    def leave_Expr(self, original_node, updated_node):
        new_node = updated_node

        if self.docstring is not None:
            if isinstance(original_node.value, cst.SimpleString):

                docstring = self.docstring
                valueInExpr = original_node.value.value

                docstring = docstring.replace('"', " ")
                docstring = docstring.strip()
                docstring = docstring.split("\n")

                valueInExpr = valueInExpr.replace('"', " ")
                valueInExpr = valueInExpr.strip()
                valueInExpr = valueInExpr.split("\n")

                new_docstringList = []
                for entry in docstring:
                    if entry != "":
                        entry = entry.strip()
                        new_docstringList.append(entry)

                new_valueInExprList = []
                for entry in valueInExpr:
                    if entry != "":
                        entry = entry.strip()
                        new_valueInExprList.append(entry)

                docstring = ",".join(new_docstringList)
                valueInExpr = ",".join(new_valueInExprList)

                new_node = cst.RemoveFromParent()

        return super().leave_Expr(original_node, new_node)


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
