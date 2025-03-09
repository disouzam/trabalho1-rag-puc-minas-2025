import os

from openai.types import file_content


def extract_source_code_from_repository(logger, repo_path):

    code_file_contents: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        print(dirpath)
        print(dirnames)
        print(filenames)

        for filename in filenames:
            if filename.endswith(".py"):
                with open(filename, mode="r", encoding="utf-8") as code_file:
                    file_content = code_file.read()
                    code_file_contents.append(file_content)

    return code_file_contents
