import PyPDF2


def extract_text_from_pdf(logger, pdf_path: str) -> str:
    logger.info("Extraindo texto do PDF: %s", pdf_path)
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except IOError as ioerror:
        logger.error("Erro ao ler o arquivo PDF: %s", ioerror)
    return text
