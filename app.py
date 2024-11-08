# app.py
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from translation_pipeline import TranslationPipeline
from final_document_assembler import FinalDocumentAssembler
from pdf_converter import convert_pdf_to_docx
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime


# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuraciones de rutas
UPLOAD_FOLDER = 'DOC'
OUTPUT_FOLDER = 'OUTPUT'

app = Flask(__name__, static_folder="static/dist")

CORS(app)  # Mueve CORS aquí, inmediatamente después de crear la instancia de Flask

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar a 16 MB por archivo

# Asegurarse de que las carpetas existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


#---route begin---
# Sirve la aplicación React en la raíz
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/<path:path>')
def serve_react_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Limpiar el contenido de checkpoint.txt
    checkpoint_path = 'checkpoint.txt'
    open(checkpoint_path, 'w').close()  # Vaciar el contenido de checkpoint.txt

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Guardar el archivo PDF
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        # Convertir el PDF a DOCX
        docx_path = pdf_path.replace('.pdf', '.docx')
        convert_pdf_to_docx(pdf_path, docx_path)
        
        # Procesar el archivo DOCX
        pipeline = TranslationPipeline(docx_path, model_name=os.getenv("MODEL_NAME"), output_dir=OUTPUT_FOLDER)
        try:
            pipeline.run()
            process_completed = True
        except Exception as e:
            print(f"Error en el proceso de traducción: {e}")
            return jsonify({'error': 'Error in translation process'}), 500
        
        # Generar el nombre del archivo final con el nombre original, fecha y hora actuales
        base_filename = os.path.splitext(filename)[0]  # Nombre del archivo sin la extensión
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_filename = f"{base_filename}_{current_time}.docx"
        
        # Crear el documento final si el proceso fue exitoso
        assembler = FinalDocumentAssembler(output_dir=OUTPUT_FOLDER)
        assembler.assemble_final_document(process_completed)
        
        # Renombrar el archivo final al nuevo nombre
        final_path = os.path.join(OUTPUT_FOLDER, final_filename)
        os.rename(os.path.join(OUTPUT_FOLDER, 'LibroFinal.docx'), final_path)
        
        # Enviar nombre de archivo final como respuesta
        return jsonify({'filename': final_filename})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Permitir la descarga del archivo procesado."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


@app.route('/processed-files', methods=['GET'])
def list_processed_files():
    """Devuelve una lista de archivos procesados en la carpeta OUTPUT."""
    files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.endswith('.docx')]
    return jsonify(files)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
