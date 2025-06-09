from flask import Flask, request, jsonify, send_from_directory
import PyPDF2
import os
import re

app = Flask(__name__)
PDF_FOLDER = 'pdfs'

def limpar_paragrafos(texto):
    return [p.strip() for p in re.split(r'\n{2,}|\r{2,}', texto) if len(p.strip()) > 30]

@app.route('/search', methods=['GET'])
def search_keywords():
    keywords_param = request.args.get('keywords')
    file_contains = request.args.get('fileContains', '').lower()

    if not keywords_param:
        return jsonify({"error": "Parâmetro 'keywords' é obrigatório."}), 400

    keywords = [k.strip().lower() for k in keywords_param.split(',')]
    resultado_final = []

    for file_name in os.listdir(PDF_FOLDER):
        if file_name.lower().endswith('.pdf') and file_contains in file_name.lower():
            file_path = os.path.join(PDF_FOLDER, file_name)
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if not text:
                        continue
                    paragrafos = limpar_paragrafos(text)
                    for k in keywords:
                        for par in paragrafos:
                            if k in par.lower():
                                resultado_final.append({
                                    "file": file_name,
                                    "page": i + 1,
                                    "paragraph": par.strip()
                                })

    return jsonify({"resultados": resultado_final})

@app.route('/openapi.yaml')
def serve_openapi():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=10000)

