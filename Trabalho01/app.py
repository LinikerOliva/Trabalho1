from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = 'bauru_participa.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_database():
    sql_create_enquetes_table = """CREATE TABLE IF NOT EXISTS enquetes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    titulo TEXT NOT NULL,
                                    descricao TEXT NOT NULL
                                );"""
    sql_create_opcoes_table = """CREATE TABLE IF NOT EXISTS opcoes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    enquete_id INTEGER NOT NULL,
                                    descricao TEXT NOT NULL,
                                    votos INTEGER DEFAULT 0,
                                    FOREIGN KEY (enquete_id) REFERENCES enquetes (id)
                                );"""
    conn = create_connection()
    if conn is not None:
        create_table(conn, sql_create_enquetes_table)
        create_table(conn, sql_create_opcoes_table)
    else:
        print("Error! Cannot create the database connection.")

create_database()

@app.route('/api/enquetes', methods=['POST'])
def criar_enquete():
    data = request.get_json()
    titulo = data['titulo']
    descricao = data['descricao']
    if titulo and descricao:
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO enquetes (titulo, descricao) VALUES (?, ?)", (titulo, descricao))
            conn.commit()
            enquete_id = cursor.lastrowid
            conn.close()
            return jsonify({"message": "Enquete criada com sucesso!", "enquete_id": enquete_id}), 201
        else:
            return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500
    else:
        return jsonify({"error": "Por favor, forneça título e descrição da enquete"}), 400

@app.route('/api/enquetes', methods=['GET'])
def listar_enquetes():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM enquetes")
        enquetes = cursor.fetchall()
        conn.close()
        return jsonify({"enquetes": enquetes}), 200
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

@app.route('/api/enquetes/<int:id>', methods=['GET'])
def obter_detalhes_enquete(id):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM enquetes WHERE id=?", (id,))
        enquete = cursor.fetchone()
        if enquete:
            cursor.execute("SELECT * FROM opcoes WHERE enquete_id=?", (id,))
            opcoes = cursor.fetchall()
            conn.close()
            return jsonify({"enquete": enquete, "opcoes": opcoes}), 200
        else:
            return jsonify({"error": "Enquete não encontrada"}), 404
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

@app.route('/api/enquetes/<int:id>/votar', methods=['POST'])
def votar_enquete(id):
    data = request.get_json()
    opcao_id = data['opcao_id']
    if opcao_id:
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("UPDATE opcoes SET votos = votos + 1 WHERE id=? AND enquete_id=?", (opcao_id, id))
            conn.commit()
            conn.close()
            return jsonify({"message": "Voto registrado com sucesso!"}), 200
        else:
            return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500
    else:
        return jsonify({"error": "Por favor, forneça a opção de voto"}), 400

@app.route('/api/enquetes/<int:id>/resultados', methods=['GET'])
def resultados_enquete(id):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opcoes WHERE enquete_id=?", (id,))
        opcoes = cursor.fetchall()
        conn.close()
        return jsonify({"opcoes": opcoes}), 200
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

@app.route('/api/enquetes/<int:id>/opcoes', methods=['GET'])
def visualizar_opcoes_enquete(id):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opcoes WHERE enquete_id=?", (id,))
        opcoes = cursor.fetchall()
        conn.close()
        return jsonify({"opcoes": opcoes}), 200
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

@app.route('/api/enquetes/<int:id>/opcoes', methods=['POST'])
def adicionar_opcao_enquete(id):
    data = request.get_json()
    descricao_opcao = data['descricao']
    if descricao_opcao:
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO opcoes (enquete_id, descricao) VALUES (?, ?)", (id, descricao_opcao))
            conn.commit()
            conn.close()
            return jsonify({"message": "Opção adicionada com sucesso!"}), 201
        else:
            return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500
    else:
        return jsonify({"error": "Por favor, forneça a descrição da opção"}), 400

@app.route('/api/enquetes/<int:id>', methods=['DELETE'])
def deletar_enquete(id):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enquetes WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Enquete deletada com sucesso!"}), 200
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

@app.route('/api/enquetes/<int:id_enquete>/opcoes/<int:id_opcao>', methods=['DELETE'])
def deletar_opcao_enquete(id_enquete, id_opcao):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM opcoes WHERE id=? AND enquete_id=?", (id_opcao, id_enquete))
        conn.commit()
        conn.close()
        return jsonify({"message": "Opção deletada com sucesso!"}), 200
    else:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

if __name__ == '__main__':
    app.run(debug=True)
