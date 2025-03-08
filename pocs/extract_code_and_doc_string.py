import ast
import sys
import logging
from src.utils.custom_logging import logger_setup

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
    logger_setup(logger, 'pocs/extract_code_and_doc_string.log')

    logger.info("===============================")
    logger.info("Início da execução")
    logger.info("")

    file_path = sys.argv[1]
    f = open(file_path, "r") #filename input
    module = ast.parse(f.read())
    class_definitions = [node for node in module.body if isinstance(node, ast.ClassDef)]
    method_definitions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    for class_def in class_definitions:

        print(class_def.name)
        logger.info(class_def.name)

        print(ast.get_docstring(class_def))
        logger.info(ast.get_docstring(class_def))

        function_definitions = [node for node in class_def.body if isinstance(node, ast.FunctionDef)]
        for f in function_definitions:
            print('\t---')
            print('\t'+f.name)
            print('\t---')
            print('\t'+'\t'.join(ast.get_docstring(f).splitlines(True)))
        print('----')

    # Read file again
    f = open(file_path, "r") #filename input
    file_content = f.read()

    for method_def in method_definitions:
        methodname = method_def.name
        print(methodname)
        logger.info(methodname)

        docstring = ast.get_docstring(method_def)
        if docstring is not None:
            print(docstring)
            logger.info(docstring)
        else:
            print(f"There is no docstring for {methodname}")
            logger.info("There is no docstring for %s", methodname)

        code_segment = ast.get_source_segment(source=file_content, node=method_def, padded=True)

        print(code_segment)
        logger.info(f"\n{code_segment}")

        print('----')
        logger.info('----')

    logger.info("Fim da execução")
    logger.info("===============================")
    logger.info("")


if __name__ == "__main__":
    main()