document.addEventListener('DOMContentLoaded', function() {
    const formElement = document.getElementById('editProposalForm');
    const tableSelect = document.getElementById('tableSelectProposal');
    const registeredTableInfo = document.querySelector('#registeredTableInfo strong');

    let tableId = '';

    for (let pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
    }

    if (formElement) {
        formElement.addEventListener('submit', function(event) {
            event.preventDefault(); // Impede o envio padrão do formulário

            const proposalId = this.dataset.proposalId;
            const formData = new FormData(this);  // Cria um novo objeto FormData

            const fileFields = [
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
                        formData.append(field, fileInput.files[i]);  // Adiciona o arquivo ao FormData
                    }
                } else {
                    // Marcar que o campo não foi alterado
                    formData.append(`${field}_no_change`, 'true');
                }
            });

            // Captura o table_id baseado no estado registrado ou seleção
            if (registeredTableInfo) {
                tableId = registeredTableInfo.dataset.tableId;
            }

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

            // Captura o valor do campo de operação
            const operationSelect = document.getElementById('operationSelect');
            const operationValue = operationSelect ? operationSelect.value : '';
            formData.append('operation_select', operationValue || null); 

            // Envia a requisição para o servidor
            fetch(`/proposal/edit-proposal/${proposalId}`, {
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
