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
                    "Serviço especializado em conserto e manutenção preventiva de geladeiras, freezers e ar-condicionados, garantindo o bom funcionamento e prolongando a vida útil dos aparelhos.",
                    "https://images.unsplash.com/photo-1709432767122-d3cb5326911a?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Segurança Eletrônica",
                    "Instalação e manutenção de sistemas de alarme, câmeras de segurança (CFTV), cercas elétricas e controle de acesso para proteger residências e comércios.",
                    "https://images.unsplash.com/photo-1589935447067-5531094415d1?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Pintor",
                    "Profissional responsável por preparar superfícies e aplicar tinta em paredes, tetos, grades e outros, com foco em acabamento, estética e proteção.",
                    "https://plus.unsplash.com/premium_photo-1675425206468-dc196f6decdc?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Marceneiro",
                    "Fabricação, montagem e reparo de móveis sob medida, como armários, estantes e mesas, além de restauração de peças de madeira.",
                    "https://images.unsplash.com/photo-1617758475736-343015e3098f?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Jardineiro",
                    "Cuida da manutenção de jardins, incluindo poda, plantio, adubação e limpeza de áreas verdes, mantendo o espaço bonito e saudável.",
                    "https://images.unsplash.com/photo-1657664042448-c955b411d9d0?q=80&w=1632&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "populares",
                ),
                (
                    "Babá",
                    "Cuidados com crianças, incluindo alimentação, higiene, recreação e acompanhamento em atividades diárias com segurança e carinho.",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3qbw6zUeP-6avqHYuQl8BPXrkX5FFCqxfBw&s",
                    1,
                    "cuidados",
                ),
                (
                    "Pedreiro",
                    "Construção, reforma e manutenção de estruturas, alvenaria, pisos, revestimentos e acabamentos em obras residenciais e comerciais.",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSm6j3j0zSda46fVRm2sdznU6tIrJJaFE3RHg&s",
                    1,
                    "cuidados",
                ),
                (
                    "Cuidador de Idosos",
                    "Acompanhamento e assistência a idosos em suas rotinas diárias, como higiene, alimentação, medicação e mobilidade, com atenção e respeito.",
                    "https://cesaitaipu.com.br/wp-content/uploads/2023/06/WhatsApp-Image-2023-06-27-at-17.13.58-2.jpeg",
                    1,
                    "cuidados",
                ),
                (
                    "Dedetizador",
                    "Aplicação de produtos e técnicas para controle e eliminação de pragas urbanas como insetos, roedores e cupins em ambientes residenciais e comerciais.",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQAmxwLiTcvnqzS0HeaPbBcX4X_2OcOOUb7Dw&s",
                    1,
                    "cuidados",
                ),
                (
                    "Limpeza Residencial",
                    "Limpeza geral e detalhada de casas e apartamentos, incluindo banheiros, cozinhas, janelas e superfícies, com foco em higiene e organização.",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuXt4Ur24UERuH5YjOIx9TBaSWEerbA0-Www&s",
                    1,
                    "cuidados",
                ),
                (
                    "Fotógrafo",
                    "Captura e edição de imagens profissionais para eventos, retratos, produtos e ensaios, com foco em qualidade visual e criatividade.",
                    "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Designer Gráfico",
                    "Criação de peças visuais como logotipos, panfletos, cartões, posts e identidades visuais, utilizando ferramentas digitais e design criativo.",
                    "https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Maquiador",
                    "Aplicação de maquiagem profissional para eventos, ensaios ou uso diário, destacando a beleza natural com técnicas personalizadas.",
                    "https://images.unsplash.com/photo-1613966802194-d46a163af70d?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    1,
                    "criativos",
                ),
                (
                    "Personal Trainer",
                    "Elaboração e acompanhamento de treinos personalizados com foco em condicionamento físico, saúde, emagrecimento ou hipertrofia.",
                    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=400&q=80",
                    1,
                    "criativos",
                ),
                (
                    "Coach de Carreira",
                    "Orientação profissional para definição de metas, transição de carreira, desenvolvimento de habilidades e planejamento de crescimento profissional.",
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
