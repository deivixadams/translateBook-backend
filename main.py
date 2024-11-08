# main.py
import os
from dotenv import load_dotenv
from translation_pipeline import TranslationPipeline
from final_document_assembler import FinalDocumentAssembler
from pdf_converter import convert_pdf_to_docx

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las rutas y configuraciones desde el archivo .env
pdf_path = os.getenv("PDF_PATH")  # Nuevo: ruta del archivo PDF en el .env
input_path = os.getenv("INPUT_PATH")
output_dir = os.getenv("OUTPUT_DIR")
model_name = os.getenv("MODEL_NAME")
pages_per_block = int(os.getenv("PAGES_PER_BLOCK", 10))

# Convertir PDF a DOCX si es necesario
if pdf_path and not os.path.exists(input_path):
    print("Convirtiendo PDF a DOCX...")
    convert_pdf_to_docx(pdf_path, input_path)
    print("Conversión completada.")

# Crear y ejecutar la tubería de traducción con las rutas y configuraciones del .env
pipeline = TranslationPipeline(input_path, model_name=model_name, output_dir=output_dir, pages_per_block=pages_per_block)
try:
    pipeline.run()
    process_completed = True
except Exception as e:
    print(f"Error en el proceso de traducción: {e}")
    process_completed = False

# Crear el documento final si el proceso fue exitoso
assembler = FinalDocumentAssembler(output_dir=output_dir)
assembler.assemble_final_document(process_completed)
