document.getElementById('deleteBanker').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const selectElement = document.getElementById('bankerId');
    const bankId = selectElement.value; 

    if (!bankId) {
        alert('O ID do banco é necessário para deletar.');
        return;
    }

    const url = `/delete-bankers/${bankId}`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message || 'Banco deletado com sucesso.');

            const optionToRemove = selectElement.querySelector(`option[value="${bankId}"]`);
            if (optionToRemove) {
                selectElement.removeChild(optionToRemove);
            }

        } else {
            alert(data.error || 'Ocorreu um erro ao deletar o banco.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocorreu um erro ao comunicar com o servidor.');
    });
});
