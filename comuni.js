let logado = false;
let usuarioLogado = "";

function abrirLogin() {
  document.getElementById('modalLogin').style.display = 'block';
}
function fecharLogin() {
  document.getElementById('modalLogin').style.display = 'none';
}
function abrirCadastro() {
  document.getElementById('modalCadastro').style.display = 'block';
}
function fecharCadastro() {
  document.getElementById('modalCadastro').style.display = 'none';
}
function cadastrarUsuario() {
  const usuario = document.getElementById('novoUsuario').value;
  const senha = document.getElementById('novaSenha').value;
  fetch('http://localhost:5000/cadastrar', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({usuario, senha})
  }).then(res => res.json()).then(data => {
    alert(data.msg);
    fecharCadastro();
  });
}
function fazerLogin() {
  const usuario = document.getElementById('usuario').value;
  const senha = document.getElementById('senha').value;
  fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({usuario, senha})
  }).then(res => res.json()).then(data => {
    if (data.status === 'ok') {
      logado = true;
      usuarioLogado = usuario;
      alert("Login realizado!");
      fecharLogin();
    } else {
      alert("Login inválido.");
    }
  });
}
function mostrarMapa() {
  document.getElementById('mapa').style.display = 'block';
  window.scrollTo(0, document.getElementById('mapa').offsetTop);
}
function enviarFeedback(e) {
  e.preventDefault();
  if (!logado) {
    alert("Faça login para enviar feedback.");
    return;
  }
  const mensagem = document.getElementById('mensagem').value;
  fetch('http://localhost:5000/feedback', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({usuario: usuarioLogado, mensagem})
  }).then(res => res.json()).then(data => {
    alert("Feedback enviado!");
    document.getElementById('mensagem').value = '';
  });
}
function verFeedbacks() {
  fetch('http://localhost:5000/feedbacks')
    .then(res => res.json())
    .then(data => {
      const lista = document.getElementById('listaFeedbacks');
      lista.innerHTML = '';
      data.forEach(f => {
        const li = document.createElement('li');
        li.textContent = f.usuario + ": " + f.mensagem;
        lista.appendChild(li);
      });
      document.getElementById('painel').style.display = 'block';
    });
}
// Carrossel funcional para múltiplas seções
document.addEventListener('DOMContentLoaded', () => {
  const carousels = document.querySelectorAll('.carousel');

  carousels.forEach(carousel => {
    const cardsContainer = carousel.querySelector('.cards');
    const prevBtn = carousel.querySelector('.prev');
    const nextBtn = carousel.querySelector('.next');
    const cardWidth = carousel.querySelector('.card').offsetWidth + 20; // largura + gap
    let scrollIndex = 0;

    prevBtn.addEventListener('click', () => {
      scrollIndex = Math.max(scrollIndex - 1, 0);
      cardsContainer.style.transform = `translateX(-${scrollIndex * cardWidth}px)`;
    });

    nextBtn.addEventListener('click', () => {
      const maxScroll = cardsContainer.children.length - Math.floor(carousel.offsetWidth / cardWidth);
      scrollIndex = Math.min(scrollIndex + 1, maxScroll);
      cardsContainer.style.transform = `translateX(-${scrollIndex * cardWidth}px)`;
    });
  });
});