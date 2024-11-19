import sqlite3
from flask import Flask, render_template, request, redirect, url_for, make_response
from importlab import Document

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('usuarios_jogos.db')
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas pelo nome
    return conn

# Função para criar as tabelas no banco de dados
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Criar tabela de jogos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jogos (
        id_jogo INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_jogo TEXT,
        desenvolvedor TEXT,
        data_lancamento DATE
    )
    ''')

    # Criar tabela de contas de jogos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contas_jogos (
        id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        id_jogo INTEGER,
        username TEXT,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        nivel INTEGER,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_jogo) REFERENCES jogos(id_jogo)
    )
    ''')

    conn.commit()
    conn.close()

# Inicializar o banco de dados (criar as tabelas)
create_tables()

# Rota para listar usuários
@app.route('/users')
def list_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('list_users.html', users=users)

# Rota para adicionar um novo usuário
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']  # Em uma aplicação real, você deve criptografar a senha

        conn = get_db_connection()
        conn.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
        conn.commit()
        conn.close()
        return redirect(url_for('list_users'))
    
    return render_template('add_user.html')

# Rota para editar um usuário
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']  # Em uma aplicação real, você deve criptografar a senha
        conn.execute('UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id_usuario = ?', (nome, email, senha, id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_users'))
    
    conn.close()
    return render_template('edit_user.html', user=user)

# Rota para deletar um usuário
@app.route('/delete_user/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_users'))

# Rota para gerar o PDF com a lista de usuários
@app.route('/gerar_pdf')
def gerar_pdf():
    # Conectar ao banco de dados e pegar a lista de usuários
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()

    # Criar o documento PDF usando importlab
    doc = Document()

    # Adicionar título
    doc.add_paragraph('Lista de Usuários', style='Title')

    # Adicionar a tabela de usuários no PDF
    table = doc.add_table(rows=1, cols=4)  # 4 colunas: ID, Nome, Email, Data de Cadastro
    table.style = 'Table Grid'

    # Cabeçalho da tabela
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'ID'
    hdr_cells[1].text = 'Nome'
    hdr_cells[2].text = 'E-mail'
    hdr_cells[3].text = 'Data de Cadastro'

    # Adicionar as linhas de usuários na tabela
    for user in users:
        row_cells = table.add_row().cells
        row_cells[0].text = str(user['id_usuario'])
        row_cells[1].text = user['nome']
        row_cells[2].text = user['email']
        row_cells[3].text = user['data_cadastro']

    # Gerar o PDF e enviar como resposta
    pdf_output = doc.render_pdf()
    
    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=usuarios.pdf'
    return response

# Rota principal
@app.route('/')
def home():
    return redirect(url_for('list_users'))

if __name__ == '__main__':
    app.run(debug=True)
