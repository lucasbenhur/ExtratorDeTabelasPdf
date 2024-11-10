from flask import Flask, request, jsonify
import pdfplumber
import tempfile
import os
from flask_cors import CORS
from pymongo import MongoClient
import re

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')  # Substitua pelo seu URI do MongoDB
db = client['extrator_de_tabelas_pdf']  # Substitua pelo nome do seu banco de dados
empreendimentosUnidadesCollection = db['empreendimentos_unidades']  # Substitua pelo nome da sua coleção

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    tables = []
    
    # Criando um arquivo temporário para salvar o PDF
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name  # Salvar o caminho antes de fechar o arquivo
        file.save(temp_file_path)  # Salva o conteúdo do arquivo

    # Abrindo o arquivo salvo com pdfplumber e extraindo as tabelas
    try:
        with pdfplumber.open(temp_file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.append(table)
    finally:
        # Removendo o arquivo temporário após usá-lo
        os.remove(temp_file_path)

    #print(json.dumps({"tables": tables}, indent=4))

    return jsonify({"tables": tables})

@app.route('/importar', methods=['POST'])
def importar():
    try:
        # Recebe o JSON enviado no corpo da requisição
        data = request.get_json()

        if 'empreendimento' not in data or data['empreendimento'].strip() == '':
            return jsonify({"message": "Informe o empreendimento"}), 400

        # Campos permitidos
        campos_permitidos = [
            "Unidade",
            "Area",
            "Valor",
            "Quartos",
            "Avaliacao",
            "Posicao",
            "Vagas"
        ]

        # Verifica se todos os campos no cabeçalho estão na lista de permitidos
        campos = ["Empreendimento"] + data['dados'][0]  # Adiciona "Empreendimento" como primeiro campo
        campos_recebidos = data['dados'][0]
        
        for campo in campos_recebidos:
            if campo not in campos_permitidos:
                return jsonify({"message": f"Campo não permitido: {campo}"}), 400

        # As linhas subsequentes contêm os dados
        for linha in data['dados'][1:]:
            # Cria um dicionário para representar o objeto, incluindo o valor de "Empreendimento"
            objeto = {"Empreendimento": data['empreendimento']}
            objeto.update({campos[i + 1]: linha[i] for i in range(len(linha))})  # Adiciona outros campos a partir de "campos"

            # Realiza o update ou insert com filtro case-insensitive para "Empreendimento" e "Unidade"
            empreendimentosUnidadesCollection.update_one(
                {
                    "Empreendimento": {"$regex": f"^{re.escape(objeto['Empreendimento'])}$", "$options": "i"},
                    "Unidade": {"$regex": f"^{re.escape(objeto['Unidade'])}$", "$options": "i"}
                },
                {"$set": objeto},  # Dados a serem atualizados
                upsert=True  # Insere caso o documento não exista
            )

        return jsonify({"message": "Dados importados com sucesso!"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
