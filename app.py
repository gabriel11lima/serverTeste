import os
import json
from flask import Flask, request, jsonify
from carteirinhas import gerar_carteirinhas  # Importa a função de geração de carteirinhas
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

# Verifique se a variável de ambiente está carregada corretamente
print("Conteúdo de GOOGLE_CREDENTIALS_JSON:", google_credentials_json)

# Certifique-se de carregar o JSON corretamente
try:
    # Substituir \\n por \n para que as quebras de linha sejam processadas corretamente
    google_credentials_json = google_credentials_json.replace("\\n", "\n")
    credentials_dict = json.loads(google_credentials_json, strict=False)
    print("Tipo de credentials_dict:", type(credentials_dict))  # Deve ser <class 'dict'>
except json.JSONDecodeError as e:
    print(f"Erro ao decodificar JSON: {e}")
    credentials_dict = None

# Função para autenticação no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    if credentials_dict:
        print("credentials_dict está presente e é um dicionário")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("ListaPresenca2025")
        sheet = spreadsheet.worksheet("Página1")
        return sheet
    else:
        raise ValueError("Credenciais inválidas")

# Rota para registrar a presença
@app.route('/validate', methods=['GET'])
def registrar_presenca():
    matricula = request.args.get('matricula').strip()
    aluno_id = request.args.get('id')

    if not matricula or not aluno_id:
        return jsonify({"error": "Parâmetros 'matricula' e 'id' são necessários"}), 400

    # Obter a planilha do Google Sheets
    try:
        sheet = autenticar_google_sheets()
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

    # Nome do aluno
    nome_aluno = request.args.get('nome', 'Aluno Desconhecido')

    # Registrar presença
    status = 'Presente'
    data_presenca = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    sheet.append_row([matricula, nome_aluno, status, data_presenca])  # Colunas: Matrícula, Nome, Presença

    return jsonify({"message": f"Presença de {nome_aluno} registrada com sucesso!"}), 200

if __name__ == "__main__":
    gerar_carteirinhas()  # Gera as carteirinhas quando o servidor iniciar
    port = int(os.environ.get('PORT', 8080))  # Usa a porta 8080, caso Railway não defina
    app.run(debug=True, host='0.0.0.0', port=port)
