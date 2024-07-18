document.addEventListener('DOMContentLoaded', function() {
    const btnLoadPromoters = document.querySelector('button[data-target="loadPromoters"]');
    const btnRegisterPromoters = document.querySelector('button[data-target="registerPromoters"]');
    const btnEditPromoters = document.querySelector('button[data-target="editPromoters"]');
    const btnDeletePromoters = document.querySelector('button[data-target="deletePromoters"]');

    
    if (btnLoadPromoters && btnRegisterPromoters && btnEditPromoters && btnDeletePromoters) {
        btnLoadPromoters.addEventListener('click', function() {
            document.getElementById('post-promoters').style.display = 'none';
            document.getElementById('search-promoters').style.display = 'block';
            document.getElementById('edit-promoters').style.display = 'none';
            document.getElementById('delete-promoters').style.display = 'none';

        });

        btnRegisterPromoters.addEventListener('click', function() {
            document.getElementById('search-promoters').style.display = 'none';
            document.getElementById('post-promoters').style.display = 'block';
            document.getElementById('edit-promoters').style.display = 'none';
            document.getElementById('delete-promoters').style.display = 'none';
        });

        btnEditPromoters.addEventListener('click', function(){
            document.getElementById('search-promoters').style.display = 'none';
            document.getElementById('post-promoters').style.display = 'none';
            document.getElementById('delete-promoters').style.display = 'none';
            document.getElementById('edit-promoters').style.display = 'block';
        });
        
        btnDeletePromoters.addEventListener('click', function() {
            document.getElementById('search-promoters').style.display = 'none';
            document.getElementById('post-promoters').style.display = 'none';
            document.getElementById('edit-promoters').style.display = 'none';
            document.getElementById('delete-promoters').style.display = 'block';

        })

    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
