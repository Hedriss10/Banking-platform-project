document.addEventListener('DOMContentLoaded', function() {
    const btnLoadPromoters = document.querySelector('button[data-target="loadPromoters"]');
    const btnRegisterPromoters = document.querySelector('button[data-target="registerPromoters"]');

    if (btnLoadPromoters && btnRegisterPromoters) {
        btnLoadPromoters.addEventListener('click', function() {
            document.getElementById('post-promoters').style.display = 'none';
            document.getElementById('search-promoters').style.display = 'block';
        });

        btnRegisterPromoters.addEventListener('click', function() {
            document.getElementById('search-promoters').style.display = 'none';
            document.getElementById('post-promoters').style.display = 'block';
        });
    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
