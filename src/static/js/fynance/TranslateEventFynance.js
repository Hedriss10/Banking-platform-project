document.addEventListener('DOMContentLoaded', function() {
    const btnListBankers = document.querySelector('button[data-target="listBankers"]');
    const btnRegisterBankers = document.querySelector('button[data-target="registerBankers"]');
    
    if (btnListBankers && btnRegisterBankers ) {
        btnListBankers.addEventListener('click', function() {
            document.getElementById('register-bankers').style.display = 'none';
            document.getElementById('list-bankers').style.display = 'block';


        });

        btnRegisterBankers.addEventListener('click', function() {
            document.getElementById('list-bankers').style.display = 'none';
            document.getElementById('register-bankers').style.display = 'block';
            document.getElementById('conven-banker').style.display = 'none';
            document.getElementById('report-banker').style.display = 'none';
            document.getElementById('delete-banker').style.display = 'none';

        });

    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
