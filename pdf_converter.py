# pdf_converter.py
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_file, docx_file):
    """
    Convierte un archivo PDF a DOCX.
    """
    cv = Converter(pdf_file)
    cv.convert(docx_file, start=0, end=None)
    cv.close()
