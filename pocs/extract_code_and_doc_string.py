import ast
import sys

def main():
    file_path = sys.argv[1]
    f = open(file_path, "r") #filename input
    module = ast.parse(f.read())
    class_definitions = [node for node in module.body if isinstance(node, ast.ClassDef)]
    method_definitions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    for class_def in class_definitions:
        print(class_def.name)
        print(ast.get_docstring(class_def))
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
        print(method_def.name)
        print(ast.get_docstring(method_def))
        code_segment = ast.get_source_segment(source=file_content, node=method_def, padded=True)
        print(code_segment)
        print('----')

if __name__ == "__main__":
    main()