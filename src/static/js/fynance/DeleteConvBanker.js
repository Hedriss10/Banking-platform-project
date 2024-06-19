// DeleteConvBanker.js
function deleteConvenio(event, element) {
    event.stopPropagation(); // Impede que o clique propague para o toggleConvenios
    const convenioId = element.getAttribute('data-id');

    if (confirm('Tem certeza que deseja deletar este convênio?')) {
        fetch(`/delete-bankers/conv/${convenioId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Convênio deletado com sucesso!');
                // Remove o item da lista
                element.parentElement.remove();
            } else {
                alert(data.message || 'Erro ao deletar convênio.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao comunicar com o servidor.');
        });
    }
}
