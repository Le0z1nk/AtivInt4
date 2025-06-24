import sqlite3
import os
from flask import Flask, request, jsonify, g, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua-chave-secreta-incrivelmente-segura"
CORS(app)
DATABASE = "banco.db"


# --- Gerenciamento do Banco de Dados ---
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, email TEXT UNIQUE)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                imagem_url TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS feedbacks (id INTEGER PRIMARY KEY, usuario_id INTEGER, mensagem TEXT, FOREIGN KEY(usuario_id) REFERENCES usuarios(id))"
        )
        db.commit()


# --- Função para Popular o Banco com Dados Iniciais ---
def populate_db_if_empty():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(id) FROM servicos")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Populando o banco de dados com serviços iniciais...")
            cursor.execute(
                "INSERT OR IGNORE INTO usuarios (id, usuario, senha, email) VALUES (?, ?, ?, ?)",
                (1, "admin", generate_password_hash("admin"), "admin@site.com"),
            )
            servicos_iniciais = [
                (
                    "Refrigeração e Manutenção",
                    "Descrição completa do serviço de refrigeração e manutenção.",
                    "https://images.unsplash.com/photo-1709432767122-d3cb5326911a?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Segurança Eletrônica",
                    "Descrição completa do serviço de segurança eletrônica.",
                    "https://images.unsplash.com/photo-1589935447067-5531094415d1?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Pintor",
                    "Descrição completa do serviço de pintura.",
                    "https://plus.unsplash.com/premium_photo-1675425206468-dc196f6decdc?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Marceneiro",
                    "Descrição completa do serviço de marcenaria.",
                    "https://images.unsplash.com/photo-1617758475736-343015e3098f?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Jardineiro",
                    "Descrição completa do serviço de jardinagem.",
                    "https://images.unsplash.com/photo-1657664042448-c955b411d9d0?q=80&w=1632&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Babá",
                    "Descrição completa do serviço de babá.",
                    "https://images.unsplash.com/photo-1585183575305-750ab15467b6?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "cuidados",
                ),
                (
                    "Pedreiro",
                    "Descrição completa do serviço de pedreiro.",
                    "https://images.unsplash.com/photo-1489514354504-1653aa90e34e?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "cuidados",
                ),
                (
                    "Cuidador de Idosos",
                    "Descrição completa do serviço de cuidador de idosos.",
                    "https://images.unsplash.com/photo-1679001976061-43be2417a90e?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "cuidados",
                ),
                (
                    "Dedetizador",
                    "Descrição completa do serviço de dedetização.",
                    "https://images.unsplash.com/photo-1581578405048-b6f813432ca4?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "cuidados",
                ),
                (
                    "Limpeza Residencial",
                    "Descrição completa do serviço de limpeza residencial.",
                    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=400&q=80",
                    1,
                    "cuidados",
                ),
                (
                    "Fotógrafo",
                    "Descrição completa do serviço de fotografia.",
                    "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Designer Gráfico",
                    "Descrição completa do serviço de design gráfico.",
                    "https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Maquiador",
                    "Descrição completa do serviço de maquiagem.",
                    "https://images.unsplash.com/photo-1613966802194-d46a163af70d?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "criativos",
                ),
                (
                    "Personal Trainer",
                    "Descrição completa do serviço de personal trainer.",
                    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Coach de Carreira",
                    "Descrição completa do serviço de coach de carreira.",
                    "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
            ]
            cursor.executemany(
                "INSERT INTO servicos (nome, descricao, imagem_url, usuario_id, categoria) VALUES (?, ?, ?, ?, ?)",
                servicos_iniciais,
            )
            db.commit()


# --- Decorator de Autenticação ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("authToken")
        if not token:
            return jsonify({"msg": "Token é necessário!"}), 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            db = get_db()
            current_user = db.execute(
                "SELECT * FROM usuarios WHERE id = ?", (data["id"],)
            ).fetchone()
            if not current_user:
                raise Exception("Usuário do token não encontrado.")
        except Exception as e:
            return (
                jsonify({"msg": "Token é inválido ou expirado!", "error": str(e)}),
                401,
            )
        return f(current_user, *args, **kwargs)

    return decorated


# --- Rotas de Páginas ---
@app.route("/")
def serve_index():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


# ### ALTERAÇÃO AQUI ###
# A função foi renomeada para corresponder ao que o template espera
@app.route("/cadastrar-servico")
def cadastrar_servico():
    return render_template("cadastrar_servico.html")


@app.route("/servico/<int:servico_id>")
def servico_detalhe(servico_id):
    db = get_db()
    servico = db.execute(
        """
        SELECT s.id, s.nome, s.descricao, s.imagem_url, u.usuario, u.email as contato_email
        FROM servicos s JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.id = ?
        """,
        (servico_id,),
    ).fetchone()
    if servico is None:
        return "Serviço não encontrado", 404
    return render_template("servico_detalhe.html", servico=servico)


# --- Rotas de API ---
@app.route("/api/servicos")
def get_servicos():
    db = get_db()
    servicos_data = db.execute("SELECT * FROM servicos ORDER BY id").fetchall()
    return jsonify([dict(row) for row in servicos_data])


@app.route("/api/cadastrar-servico", methods=["POST"])
@token_required
def cadastrar_servico_api(current_user):
    data = request.get_json()
    nome = data.get("nome")
    imagem_url = data.get("imagem_url")
    descricao = data.get("descricao")
    categoria = data.get("categoria")

    if not all([nome, imagem_url, descricao, categoria]):
        return jsonify({"msg": "Todos os campos são obrigatórios!"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO servicos (nome, descricao, imagem_url, usuario_id, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, imagem_url, current_user["id"], categoria),
    )
    db.commit()
    return jsonify({"msg": "Serviço cadastrado com sucesso!"}), 201


@app.route("/api/cadastrar", methods=["POST"])
def cadastrar_usuario():
    data = request.get_json()
    if (
        not data
        or not data.get("usuario")
        or not data.get("senha")
        or not data.get("email")
    ):
        return jsonify({"msg": "Usuário, senha e email são obrigatórios."}), 400

    usuario = data["usuario"]
    email = data["email"]
    senha_hash = generate_password_hash(data["senha"])

    try:
        db = get_db()
        db.execute(
            "INSERT INTO usuarios (usuario, email, senha) VALUES (?, ?, ?)",
            (usuario, email, senha_hash),
        )
        db.commit()
        return jsonify({"msg": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"msg": "Usuário ou e-mail já existe."}), 409


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("usuario") or not data.get("senha"):
        return jsonify({"msg": "Usuário e senha são obrigatórios."}), 400

    db = get_db()
    user_data = db.execute(
        "SELECT * FROM usuarios WHERE usuario = ?", (data["usuario"],)
    ).fetchone()

    if user_data and check_password_hash(user_data["senha"], data["senha"]):
        token = jwt.encode(
            {
                "id": user_data["id"],
                "usuario": user_data["usuario"],
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        resp = jsonify({"status": "ok"})
        resp.set_cookie(
            "authToken", token, httponly=True, samesite="Lax", max_age=86400
        )
        return resp

    return jsonify({"status": "erro", "msg": "Usuário ou senha inválidos."}), 401


@app.route("/api/check-status")
@token_required
def check_status(current_user):
    return jsonify({"logged_in": True, "usuario": current_user["usuario"]})


@app.route("/api/feedback", methods=["POST"])
@token_required
def feedback_api(current_user):
    data = request.get_json()
    if not data or not data.get("mensagem"):
        return jsonify({"msg": "A mensagem de feedback é obrigatória."}), 400

    db = get_db()
    db.execute(
        "INSERT INTO feedbacks (usuario_id, mensagem) VALUES (?, ?)",
        (current_user["id"], data["mensagem"]),
    )
    db.commit()
    return jsonify({"status": "ok", "msg": "Feedback recebido!"})


@app.route("/api/feedbacks", methods=["GET"])
def get_feedbacks():
    db = get_db()
    feedbacks_data = db.execute(
        """
        SELECT f.mensagem, u.usuario FROM feedbacks f
        JOIN usuarios u ON f.usuario_id = u.id
        ORDER BY f.id DESC
        """
    ).fetchall()
    return jsonify([dict(row) for row in feedbacks_data])


@app.route("/api/logout", methods=["POST"])
def logout():
    resp = jsonify({"status": "ok"})
    resp.set_cookie("authToken", "", expires=0)
    return resp


if __name__ == "__main__":
    init_db()
    populate_db_if_empty()
    app.run(debug=True, port=5000)
