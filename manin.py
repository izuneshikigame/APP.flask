import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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

# Rota principal
@app.route('/')
def home():
    return redirect(url_for('list_users'))

from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# Inicializar a aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

# Rota para a página de listagem
@app.route('/usuarios')
def list_users():
    users = Usuario.query.all()
    return render_template('list_users.html', users=users)

# Função para gerar o PDF usando ReportLab
def generate_pdf(users):
    # Criar um objeto BytesIO para gerar o PDF em memória
    buffer = BytesIO()

    # Criar o canvas do PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Tamanho da página (letra: 612x792 pontos)

    # Definir fonte
    c.setFont("Helvetica", 12)

    # Adicionar título
    c.drawString(200, height - 40, "Lista de Usuários")

    # Adicionar cabeçalho da tabela
    c.drawString(30, height - 80, "ID")
    c.drawString(100, height - 80, "Nome")
    c.drawString(300, height - 80, "E-mail")
    c.drawString(500, height - 80, "Data de Cadastro")

    # Adicionar dados dos usuários na tabela
    y_position = height - 100
    for user in users:
        if y_position < 60:  # Se a página acabar, adicionar uma nova página
            c.showPage()
            c.setFont("Helvetica", 12)
            c.drawString(200, height - 40, "Lista de Usuários")
            c.drawString(30, height - 80, "ID")
            c.drawString(100, height - 80, "Nome")
            c.drawString(300, height - 80, "E-mail")
            c.drawString(500, height - 80, "Data de Cadastro")
            y_position = height - 100

        c.drawString(30, y_position, str(user.id_usuario))
        c.drawString(100, y_position, user.nome)
        c.drawString(300, y_position, user.email)
        c.drawString(500, y_position, user.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'))
        
        y_position -= 20  # Ajuste de espaçamento entre as linhas

    # Salvar o PDF
    c.save()

    # Obter o PDF gerado e retornar
    buffer.seek(0)
    return buffer

# Rota para gerar o PDF
@app.route('/gerar_pdf')
def gerar_pdf():
    users = Usuario.query.all()
    pdf = generate_pdf(users)

    # Criar a resposta com o PDF
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=usuarios.pdf'
    return response

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
