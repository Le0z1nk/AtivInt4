// --- INICIALIZAÇÃO ---
// Um único listener que executa quando a página carrega, sem duplicação.
document.addEventListener("DOMContentLoaded", () => {
  // A função verificarLogin agora é a primeira coisa a ser chamada para montar o menu corretamente.
  verificarLogin();

  // Funções específicas da página principal
  if (document.getElementById("cards-populares")) {
    carregarServicos();
  }
  if (document.getElementById("listaFeedbacks")) {
    carregarFeedbacks();
  }

  // Configura o formulário da página de cadastro de serviço, se ele existir
  const formCadastroServico = document.getElementById("form-cadastro-servico");
  if (formCadastroServico) {
    formCadastroServico.addEventListener("submit", cadastrarServico);
  }

  // Lógica para todos os carrosséis da página
  document.querySelectorAll(".carousel").forEach(setupCarousel);
});

// --- Lógica de Autenticação e API (VERSÃO CORRIGIDA COM COOKIES) ---

const API_BASE_URL = "/api";

/**
 * Verifica o status de login chamando a API e atualiza o menu de navegação.
 * Esta é a forma correta de trabalhar com cookies httpOnly.
 */
async function verificarLogin() {
  const navLinks = document.querySelector(".nav-links");
  if (!navLinks) return;

  try {
    const response = await fetch(`${API_BASE_URL}/check-status`);

    let menuHTML = "";
    if (response.ok) {
      const data = await response.json();
      // Menu para usuários LOGADOS
      menuHTML = `
                <li><span class="welcome-user">Olá, ${data.usuario}!</span></li>
                <li><a href="/cadastrar-servico">Cadastrar Serviço</a></li>
                <li><a href="#" onclick="logout()">Sair</a></li>
            `;
    } else {
      // Menu para usuários DESLOGADOS
      menuHTML = `
                <li><a href="/login">Login</a></li>
                <li><a href="#" onclick="abrirCadastro()">Cadastro</a></li>
                <li><a href="#" onclick="mostrarMapa()">Mapa</a></li>
                <li><a href="#feedback">Feedback</a></li>
            `;
    }
    navLinks.innerHTML = menuHTML;
  } catch (error) {
    console.error("Erro ao verificar status de login:", error);
    // Garante que o menu de deslogado apareça em caso de erro de rede
    navLinks.innerHTML = `
            <li><a href="/login">Login</a></li>
            <li><a href="#" onclick="abrirCadastro()">Cadastro</a></li>
            <li><a href="#" onclick="mostrarMapa()">Mapa</a></li>
            <li><a href="#feedback">Feedback</a></li>
        `;
  }
}

/**
 * Lida com o login do usuário. Agora apenas checa a resposta do servidor.
 */
async function fazerLogin(event) {
  event.preventDefault();
  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, senha }),
    });

    if (response.ok) {
      window.location.href = "/"; // Sucesso! O cookie foi criado pelo backend. Redireciona para a home.
    } else {
      const data = await response.json();
      alert(data.msg || "Erro ao fazer login.");
    }
  } catch (error) {
    alert("Não foi possível conectar ao servidor.");
    console.error("Falha na requisição de login:", error);
  }
  return false;
}

/**
 * Lida com o logout do usuário, chamando a API de logout que limpa o cookie.
 */
async function logout() {
  await fetch(`${API_BASE_URL}/logout`, { method: "POST" });
  window.location.href = "/"; // Redireciona e a UI será atualizada para o estado "deslogado".
}

// --- Funções de Conteúdo (Carregar Serviços, Feedbacks, etc.) ---

async function carregarServicos() {
  try {
    const response = await fetch("/api/servicos");
    const servicos = await response.json();

    const containers = {
      populares: document.getElementById("cards-populares"),
      cuidados: document.getElementById("cards-cuidados"),
      criativos: document.getElementById("cards-criativos"),
    };
    // Limpa todos os containers antes de preencher
    Object.values(containers).forEach((c) => {
      if (c) c.innerHTML = "";
    });

    servicos.forEach((servico) => {
      const container = containers[servico.categoria];
      if (container) {
        const cardLink = document.createElement("a");
        cardLink.href = `/servico/${servico.id}`;
        cardLink.className = "card-link"; // Classe para remover o estilo de link

        cardLink.innerHTML = `
                    <div class="card">
                        <img src="${servico.imagem_url}" alt="${servico.nome}">
                        <div class="card-title">${servico.nome}</div>
                    </div>
                `;
        container.appendChild(cardLink);
      }
    });
  } catch (error) {
    console.error("Erro ao carregar serviços:", error);
  }
}

async function carregarFeedbacks() {
  try {
    const response = await fetch(`${API_BASE_URL}/feedbacks`);
    const feedbacks = await response.json();
    const lista = document.getElementById("listaFeedbacks");
    if (!lista) return;

    lista.innerHTML = "";
    if (feedbacks.length === 0) {
      lista.innerHTML = "<li>Nenhum feedback ainda. Seja o primeiro!</li>";
    } else {
      feedbacks.forEach((fb) => {
        const item = document.createElement("li");
        item.innerHTML = `<strong>${fb.usuario}:</strong> ${fb.mensagem}`;
        lista.appendChild(item);
      });
    }
  } catch (error) {
    console.error("Falha ao carregar feedbacks:", error);
  }
}

// --- Funções do Template (Modais, Cadastro, Carrossel) ---

/**
 * Cadastra um novo usuário.
 */
async function cadastrarUsuario() {
  const usuario = document.getElementById("novoUsuario").value;
  const email = document.getElementById("novoEmail").value;
  const senha = document.getElementById("novaSenha").value;

  if (!usuario || !email || !senha) {
    alert("Por favor, preencha todos os campos.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/cadastrar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, email, senha }),
    });
    const data = await response.json();
    alert(data.msg);
    if (response.ok) {
      fecharCadastro();
    }
  } catch (error) {
    console.error("Falha na requisição de cadastro:", error);
    alert("Não foi possível conectar ao servidor.");
  }
}

/**
 * Envia um novo feedback. Não precisa mais do token, o navegador envia o cookie.
 */
async function enviarFeedback(event) {
  event.preventDefault();
  const mensagem = document.getElementById("mensagem").value;

  try {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem }),
    });

    // Se o token for inválido/expirado, o backend retorna 401
    if (response.status === 401) {
      alert(
        "Sua sessão expirou ou você não está logado. Por favor, faça o login novamente."
      );
      window.location.href = "/login";
      return;
    }

    const data = await response.json();
    alert(data.msg);
    if (response.ok) {
      document.getElementById("mensagem").value = "";
      carregarFeedbacks();
    }
  } catch (error) {
    console.error("Falha na requisição de feedback:", error);
  }
  return false;
}

/**
 * Cadastra um novo serviço a partir do formulário.
 */
async function cadastrarServico(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await fetch(`${API_BASE_URL}/cadastrar-servico`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    if (response.ok) {
      alert(result.msg);
      window.location.href = "/";
    } else {
      if (response.status === 401) {
        alert(
          "Sua sessão expirou ou você não está logado. Por favor, faça o login novamente."
        );
        window.location.href = "/login";
      } else {
        alert(result.msg);
      }
    }
  } catch (error) {
    alert("Erro ao cadastrar serviço.");
  }
}

// Funções de UI (modais, carrossel, etc.)
function abrirCadastro() {
  const modal = document.getElementById("modalCadastro");
  if (modal) modal.style.display = "block";
}
function fecharCadastro() {
  const modal = document.getElementById("modalCadastro");
  if (modal) modal.style.display = "none";
}

function abrirModalServico(titulo, descricao) {
  const modal = document.getElementById("modalServico");
  if (modal) {
    document.getElementById("servicoTitulo").innerText = titulo;
    document.getElementById("descricaoServico").innerText = descricao;
    modal.style.display = "block";
  }
}

function fecharModalServico() {
  const modal = document.getElementById("modalServico");
  if (modal) modal.style.display = "none";
}

function mostrarMapa() {
  // Implemente a lógica do mapa ou mostre um alerta
  alert("Funcionalidade do mapa a ser implementada!");
}

function enviarContratacao(event) {
  event.preventDefault();
  alert("Contratação enviada com sucesso!");
  fecharModalServico();
}

function setupCarousel(carousel) {
  const cards = carousel.querySelector(".cards");
  const prevBtn = carousel.querySelector(".prev");
  const nextBtn = carousel.querySelector(".next");
  if (!cards || !prevBtn || !nextBtn) return;

  nextBtn.addEventListener("click", () => {
    cards.scrollBy({ left: cards.clientWidth, behavior: "smooth" });
  });

  prevBtn.addEventListener("click", () => {
    cards.scrollBy({ left: -cards.clientWidth, behavior: "smooth" });
  });
}
