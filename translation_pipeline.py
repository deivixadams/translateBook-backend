# translation_pipeline.py
from translator_model import TranslatorModel
from docx_processor import DocxProcessor

class TranslationPipeline:
    """
    Clase principal que coordina la traducción de un archivo DOCX usando TranslatorModel y DocxProcessor.
    """
    def __init__(self, input_path, model_name='Helsinki-NLP/opus-mt-en-es', output_dir="OUTPUT", pages_per_block=10):
        self.translator_model = TranslatorModel(model_name)
        self.doc_processor = DocxProcessor(input_path, self.translator_model, output_dir)
        self.pages_per_block = pages_per_block

    def run(self):
        """
        Ejecuta el proceso de traducción dividiendo el documento en bloques.
        """
        self.doc_processor.process_in_blocks(self.pages_per_block)
