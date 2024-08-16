document.addEventListener('DOMContentLoaded', function() {
    const btnListBankers = document.querySelector('button[data-target="listpermissions"]');
    const btnRegisterBankers = document.querySelector('button[data-target="edit-permissions"]');
    
    if (btnListBankers && btnRegisterBankers ) {
        btnListBankers.addEventListener('click', function() {
            document.getElementById('list-permissions').style.display = 'block';
            document.getElementById('edit-permissions').style.display = 'none';


        });

        btnRegisterBankers.addEventListener('click', function() {
            document.getElementById('list-permissions').style.display = 'none';
            document.getElementById('edit-permissions').style.display = 'block';
        });

    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
