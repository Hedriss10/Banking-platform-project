document.addEventListener('DOMContentLoaded', function() {
    const formElement = document.getElementById('editProposalForm');
    const tableSelect = document.getElementById('tableSelectProposal');
    const registeredTableInfo = document.querySelector('#registeredTableInfo strong');

    let tableId = '';

    // Captura o table_id se existir
    if (registeredTableInfo) {
        tableId = registeredTableInfo.dataset.tableId; // Pega o data-table-id
    }

    console.log("Captured tableId:", tableId); // Verifique se o valor é correto

    if (formElement) {
        formElement.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(this);

            if (tableId) {
                formData.append('table_id', tableId); 
            } else if (tableSelect) {
                const selectedTableId = tableSelect.value;
                if (selectedTableId) {
                    formData.append('table_id', selectedTableId);
                } else {
                    formData.append('table_id', null); 
                }
            } else {
                formData.append('table_id', null); 
            }

            const operationSelect = document.getElementById('operationSelect');
            const operationValue = operationSelect ? operationSelect.value : '';
            formData.append('operation_select', operationValue || null); 

            fetch(`/proposal/edit-proposal/${this.dataset.proposalId}`, {
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
                if (data) {
                    alert('Proposta atualizada com sucesso!');
                    window.location.href = "/proposal-status";
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
