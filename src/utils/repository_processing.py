import os

from openai.types import file_content


def extract_source_code_from_repository(logger, repo_path):

    code_file_contents: list[str] = []
    file_names: list[str] = get_all_python_files_from_repository(logger, repo_path)

    files_processed = 0
    for file_name in file_names:

        with open(file_name, mode="r", encoding="utf-8") as code_file:
            file_content = code_file.read()
            code_file_contents.append(file_content)

        # TODO: Para remover depois
        if files_processed == 5:
            break

    return code_file_contents, file_names


def get_all_python_files_from_repository(logger, repo_path):

    file_names: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_path):

        for filename in filenames:

            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename)
                file_names.append(fullpath)

    return file_names
