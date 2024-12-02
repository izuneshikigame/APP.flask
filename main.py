import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Banco de Dados para Usuários
def get_auth_db_connection():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_auth_tables():
    conn = get_auth_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('usuarios_jogos.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jogos (
        id_jogo INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_jogo TEXT,
        desenvolvedor TEXT,
        data_lancamento DATE
    )
    ''')

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


create_auth_tables()
create_tables()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_auth_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id_usuario']
            session['user_name'] = user['nome']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('list_users'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hashed = generate_password_hash(senha)

        try:
            conn = get_auth_db_connection()
            conn.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha_hashed))
            conn.commit()
            conn.close()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email já cadastrado.', 'danger')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    return render_template('list_users.html', user_name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


@app.route('/users')
def list_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('list_users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o email já existe no banco
        user = cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

        if user:
            flash('Erro: Email já cadastrado.', 'danger')
            conn.close()
            return render_template('add_user.html')



        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
            (nome, email, senha)
        )
        conn.commit()
        conn.close()

        flash('Usuário adicionado com sucesso!', 'success')
        return redirect(url_for('list_users'))

    return render_template('add_user.html')

@app.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,)).fetchone()

    if not user:
        conn.close()
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('list_users'))

    conn.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id,))
    conn.commit()
    conn.close()

    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('list_users'))


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id,)).fetchone()

    if not user:
        conn.close()
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn.execute(
            'UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id_usuario = ?',
            (nome, email, senha, id)
        )
        conn.commit()
        conn.close()

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('list_users'))

    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/gerar_pdf')
def gerar_pdf():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("Lista de Usuários")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, height - 40, "Lista de Usuários")
    pdf.setFont("Helvetica", 12)

    x = 30
    y = height - 80
    pdf.drawString(x, y, "ID")
    pdf.drawString(x + 50, y, "Nome")
    pdf.drawString(x + 200, y, "E-mail")
    pdf.drawString(x + 400, y, "Data de Cadastro")
    y -= 20

    for user in users:
        pdf.drawString(x, y, str(user['id_usuario']))
        pdf.drawString(x + 50, y, user['nome'])
        pdf.drawString(x + 200, y, user['email'])
        pdf.drawString(x + 400, y, user['data_cadastro'])
        y -= 20
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='usuarios.pdf', mimetype='application/pdf')

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
