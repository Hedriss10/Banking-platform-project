document.addEventListener('DOMContentLoaded', function() {
    const proposalForm = document.querySelector('form[data-proposal-id]');

    if (proposalForm) {
        const proposalId = proposalForm.dataset.proposalId;

        // Captura todos os botões de remoção de imagem
        document.querySelectorAll('.remove-image').forEach(button => {
            button.addEventListener('click', function() {
                const field = this.dataset.field;
                const path = this.dataset.path;

                if (confirm('Tem certeza que deseja remover esta imagem?')) {
                    fetch(`/proposal/remove-image/${proposalId}`, {  
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({ field: field, path: path })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Remove a imagem e o botão do DOM
                            const wrapper = this.closest('.img-wrapper');
                            if (wrapper) {
                                wrapper.remove();  // Remove o container da imagem
                            }
                        } else {
                            alert(data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao remover imagem:', error);
                        alert('Erro ao remover a imagem. Tente novamente.');
                    });
                }
            });
        });
    } else {
        console.error('Elemento de formulário não encontrado ou o ID da proposta está ausente.');
    }
});
