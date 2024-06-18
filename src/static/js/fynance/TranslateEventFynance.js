document.addEventListener('DOMContentLoaded', function() {
    const btnListBankers = document.querySelector('button[data-target="listBankers"]');
    const btnRegisterBankers = document.querySelector('button[data-target="registerBankers"]');
    const btnConvBankers = document.querySelector('button[data-target="convenBankers"]');
    const btnReporBankers = document.querySelector('button[data-target="reportBankers"]');
    const btnDeleteBankers = document.querySelector('button[data-target="deleteBankers"]');


    
    if (btnListBankers && btnRegisterBankers && btnConvBankers && btnReporBankers && btnDeleteBankers) {
        btnListBankers.addEventListener('click', function() {
            document.getElementById('register-bankers').style.display = 'none';
            document.getElementById('list-bankers').style.display = 'block';
            document.getElementById('conven-banker').style.display = 'none';
            document.getElementById('report-banker').style.display = 'none';
            document.getElementById('delete-banker').style.display = 'none';


        });

        btnRegisterBankers.addEventListener('click', function() {
            document.getElementById('list-bankers').style.display = 'none';
            document.getElementById('register-bankers').style.display = 'block';
            document.getElementById('conven-banker').style.display = 'none';
            document.getElementById('report-banker').style.display = 'none';
            document.getElementById('delete-banker').style.display = 'none';

        });

        btnConvBankers.addEventListener('click', function(){
            document.getElementById('list-bankers').style.display = 'none';
            document.getElementById('register-bankers').style.display = 'none';
            document.getElementById('report-banker').style.display = 'none';
            document.getElementById('conven-banker').style.display = 'block';
            document.getElementById('delete-banker').style.display = 'none';

        });
        
        btnReporBankers.addEventListener('click', function() {
            document.getElementById('list-bankers').style.display = 'none';
            document.getElementById('register-bankers').style.display = 'none';
            document.getElementById('conven-banker').style.display = 'none';
            document.getElementById('report-banker').style.display = 'block';
            document.getElementById('delete-banker').style.display = 'none';


        });

        btnDeleteBankers.addEventListener('click', function(){
            document.getElementById('list-bankers').style.display = 'none';
            document.getElementById('register-bankers').style.display = 'none';
            document.getElementById('conven-banker').style.display = 'none';
            document.getElementById('report-banker').style.display = 'none';
            document.getElementById('delete-banker').style.display = 'block';

        })

    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
