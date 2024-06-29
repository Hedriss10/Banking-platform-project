document.addEventListener('DOMContentLoaded', function() {
    const btnListProposal = document.querySelector('button[data-target="listProposal"]');
    const btnStatusProposal = document.querySelector('button[data-target="StatusProposal"]');
    
    if (btnListProposal && btnStatusProposal ) {
        btnListProposal.addEventListener('click', function() {
            document.getElementById('list-proposal').style.display = 'block';
            document.getElementById('status-proposal').style.display = 'none';

        });

        btnStatusProposal.addEventListener('click', function() {
            document.getElementById('status-proposal').style.display = 'block';
            document.getElementById('list-proposal').style.display = 'none';

        });

    } else {
        console.error('Os botões não foram encontrados no DOM');
    }
});
