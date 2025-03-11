# Autor:

208573 - Dickson Souza

# Sobre

Esse repositório contém customizações do projeto original do [professor Samuel Cardoso](https://github.com/samuelcardoso) para a demonstração prática do uso da técnica Retrieval Augmented Generation aplicada à Engenharia de Software.

O repositório original pode ser encontrado no link https://github.com/samuelcardoso/genai-rag e há também um fork no meu perfil pessoal em https://github.com/disouzam/genai-rag.

# Configuração

A gestão de dependências e ambientes virtuais é feita através do Poetry, embora qualquer outro gerenciador de dependência possa ser usado.

```shell
#  Criação do ambiente virtual e instalação das dependências
poetry install --no-root
```

Após o ambiente virtual estar criado, ativa-se o ambiente virtual no terminal através do seguinte comando:

```shell
# Ativação do shell com o ambiente virtual
poetry shell
```

O projeto foi desenvolvido e testado usando Python 3.12.7.

As bibliotecas em uso para criação de embeddings, processamento da árvore sintática e geração e armazenamento dos índices são:

1. [libcst, versão 1.6.0](https://pypi.org/project/libcst/)
2. [openai, versão 1.6.4](https://pypi.org/project/openai/)
3. [faiss-cpu, versão 1.10.0](https://pypi.org/project/faiss-cpu/)
4. [numpy, versão 2.2.3](https://pypi.org/project/numpy/)
5. [python-dotenv, versão 1.0.1](https://pypi.org/project/python-dotenv/)

# Depuração e execução

Todas as aplicações desenvolvidas aqui são aplicações de linha de comando. Muitas POCs foram feitas para chegar na aplicação final contida no arquivo `src\main.py`

Os comandos podem ser obtidos a partir do arquivo `.vscode\launch.json` e para a aplicação principal o comando para execução é:

```shell
poetry shell
cd src
python -m main
```

A aplicação, em sua configuração atual, está formatada para analisar o repositório `ydata-profiling` situado um nível acima desse repositório aqui mas essa configuração pode ser facilmente modificada dentro do arquivo `.env` na variável `REPOSITORY_1_PATH`

```
repos/
|
|---genai-rag/
|   |---.env
|   |---src/
|   |   |---main.py <<< Arquivo-fonte principal da aplicação
|---ydata-profiling/
|---|---src/ <<< Pasta analisada
```

```python
    (...)
    load_dotenv()
    code_repository_path = os.getenv("REPOSITORY_1_PATH")
    (...)
```

# Logging

A aplicação faz uso extenso de logging e os logs em arquivos usam sistema de arquivo rotativo com a rotação feita a cada execução para facilitar identificar diferentes testes ou simulações de cenário.
