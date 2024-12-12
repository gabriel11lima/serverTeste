import json
import os
from datetime import datetime

from flask import Flask, request, jsonify
from oauth2client.service_account import ServiceAccountCredentials
import gspread

app = Flask(__name__)

# Carregar as credenciais do Google a partir da variável de ambiente
google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')


# Função para autenticação no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Converte a string JSON para um dicionário
    creds_dict = json.loads(google_credentials_json)

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("ListaPresenca2025")
    sheet = spreadsheet.worksheet("Página1")
    return sheet


# Rota para registrar a presença
@app.route('/validate', methods=['GET'])
def registrar_presenca():
    matricula = request.args.get('matricula').strip()
    aluno_id = request.args.get('id')

    if not matricula or not aluno_id:
        return jsonify({"error": "Parâmetros 'matricula' e 'id' são necessários"}), 400

    # Obter a planilha do Google Sheets
    sheet = autenticar_google_sheets()

    # Nome do aluno
    nome_aluno = request.args.get('nome', 'Aluno Desconhecido')

    # Registrar presença
    status = 'Presente'
    data_presenca = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    sheet.append_row([matricula, nome_aluno, status, data_presenca])  # Colunas: Matrícula, Nome, Presença

    return jsonify({"message": f"Presença de {nome_aluno} registrada com sucesso!"}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
