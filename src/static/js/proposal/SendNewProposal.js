document.addEventListener('DOMContentLoaded', function () {
    var proposalForm = document.getElementById('proposalForm');

    proposalForm.addEventListener('submit', function (event) {
        event.preventDefault(); 
        var formData = new FormData(proposalForm);

        fetch('/proposal/new-proposal', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Contrato registrado com sucesso!');
                window.location.href = "/home";
            } else {
                alert(data.message || 'Erro ao deletar convênio.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('estou aqui.');
        });
    })
});