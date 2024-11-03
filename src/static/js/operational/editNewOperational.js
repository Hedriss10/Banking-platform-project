document.addEventListener('DOMContentLoaded', function() {
    const formElement = document.getElementById('editProposalForm');
    const searchInput = document.getElementById('tableSearchInput');
    const tableSelect = document.getElementById('tableSelectProposal');

    if (searchInput && tableSelect) {
        searchInput.addEventListener('input', function() {
            const searchValue = searchInput.value.toLowerCase();

            const options = tableSelect.querySelectorAll('.table-options');
            options.forEach(option => {
                const tableCode = option.textContent.toLowerCase();
                if (tableCode.includes(searchValue)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            }); 
        });
    } else {
        console.error("Campo de busca ou select de tabela não encontrado!");
    }

    if (formElement) {
        formElement.addEventListener('submit', function(event) {
            event.preventDefault();

            const proposalId = this.dataset.proposalId;
            const formData = new FormData(this);  

            var fileFields = [
                'rg_cnh_completo',
                'rg_frente',
                'rg_verso',
                'contracheque',
                'extrato_consignacoes',
                'comprovante_residencia',
                'selfie',
                'comprovante_bancario',
                'detalhamento_inss',
                'historico_consignacoes_inss'
            ];

            fileFields.forEach(function(field) {
                const fileInput = document.getElementById(field);
                if (fileInput && fileInput.files.length > 0) {
                    for (let i = 0; i < fileInput.files.length; i++) {
                        formData.append(field, fileInput.files[i]);
                    }
                } else {
                    // Marcar que o campo não foi alterado
                    formData.append(`${field}_no_change`, 'true');
                }
            });

            fetch(`/operational/edit-proposal/${proposalId}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao salvar a proposta.');
                }
                return response.json();
            })
            .then(data => {
                if (data.success ) {
                    alert('Proposta atualizada com sucesso!');
                    window.location.href = "/state-contract";
                } else {
                    alert('Erro ao atualizar proposta.');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao enviar o formulário.');
            });
        });
    } else {
        console.error("Elemento do formulário não encontrado!");
    }
});