const carousels = document.querySelectorAll('.carousel');

carousels.forEach(carousel => {
    const prev = carousel.querySelector('.prev');
    const next = carousel.querySelector('.next');
    const cards = carousel.querySelector('.cards');

    let currentIndex = 0;

    prev.addEventListener('click', () => {
        const cardWidth = carousel.querySelector('.card').offsetWidth + 20;
        currentIndex = Math.max(currentIndex - 1, 0);
        cards.style.transform = `translateX(-${cardWidth * currentIndex}px)`;
    });

    next.addEventListener('click', () => {
        const cardWidth = carousel.querySelector('.card').offsetWidth + 20;
        const totalCards = cards.children.length;
        const maxIndex = totalCards - Math.floor(carousel.offsetWidth / cardWidth);
        currentIndex = Math.min(currentIndex + 1, maxIndex);
        cards.style.transform = `translateX(-${cardWidth * currentIndex}px)`;
    });
});
