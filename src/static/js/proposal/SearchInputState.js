document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const baseUrl = document.getElementById('baseUrl').getAttribute('data-url').replace('0', ''); // Base URL do Flask para editar

    // Função para buscar propostas
    function fetchProposals(searchTerm = '') {
        fetch(`/proposal-status?search=${searchTerm}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = ''; // Limpa as linhas existentes

            if (data.length === 0) {
                const emptyRow = document.createElement('tr');
                emptyRow.innerHTML = `
                    <td colspan="11" class="text-center">Nenhuma proposta encontrada</td>  <!-- Ajuste para colspan correto -->
                `;
                tbody.appendChild(emptyRow);
                return;
            }

            data.forEach((p) => {
                const row = document.createElement('tr');
                row.setAttribute('data-proposal-id', p.id); // Adiciona um identificador à linha


                row.innerHTML = `
                    <td>${p.creator_name}</td> <!-- Nome do digitador -->
                    <td>${p.name}</td> <!-- Nome do contrato -->
                    <td>${p.created_at}</td> <!-- Data de criação -->
                    <td>${p.cpf}</td> <!-- CPF -->
                    <td>${p.operation_select}</td>
                    <td>
                        ${p.aguardando_digitacao ? '<span class="badge bg-secondary">AGUARDANDO A DIGITAÇÃO</span>' : ''}
                        ${p.pendente_digitacao ? '<span class="badge bg-warning">PENDENTE DIGITAÇÃO</span>' : ''}
                        ${p.contrato_digitacao ? '<span class="badge bg-secondary">CONTRATO EM DIGITAÇÃO</span>' : ''}
                        ${p.aguardando_aceite_do_cliente ? '<span class="badge bg-secondary">AGUARDANDO O ACEITE DO CLIENTE</span>' : ''}
                        ${p.aceite_feito_analise_do_banco ? '<span class="badge bg-secondary">ACEITE FEITO EM ANÁLISE DO BANCO</span>' : ''}
                        ${p.contrato_pendente_pelo_banco ? '<span class="badge bg-secondary">CONTRATO PENDENTE PELO BANCO</span>' : ''}
                        ${p.aguardando_pagamento ? '<span class="badge bg-dark">AGUARDANDO O PAGAMENTO</span>' : ''}
                        ${p.contratopago ? '<span class="badge bg-success">CONTRATO PAGO</span>' : ''}
                    </td>
                    <td>
                        <span class="badge bg-warning">
                            <a href="${baseUrl}${p.id}">Editar</a> <!-- Usando a base URL do Flask -->
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-danger delete-proposal" data-id="${p.id}" style="cursor:pointer;">Excluir</span>
                    </td>
                    <td>${p.edit_at}</td> <!-- Editado por --> 
                    <td>${p.completed_at}</td>
                    <td>${p.completed_by}</td>
                `;
                tbody.appendChild(row);
            });

            // Após popular a tabela, adicionar os listeners para exclusão
            addDeleteListeners();
        })
        .catch(error => console.error('Erro ao buscar dados:', error));
    }

    function addDeleteListeners() {
        document.querySelectorAll('.delete-proposal').forEach(button => {
            button.addEventListener('click', function() {
                const proposalId = this.getAttribute('data-id');

                if (confirm('Tem certeza que deseja excluir esta proposta?')) {
                    fetch(`/proposal/delete-proposal/${proposalId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => response.json())  // Diretamente convertendo a resposta em JSON
                    .then(data => {
                        if (data.success) {
                            alert('Proposta excluída com sucesso!');
                            // Atualiza a tabela após a exclusão
                            fetchProposals(searchInput.value.toLowerCase());
                        } else {
                            alert('Erro ao excluir a proposta: ' + (data.error || 'Erro desconhecido.'));
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao excluir a proposta:', error);
                        alert('Não foi possível excluir a proposta.');
                    });
                }
            });
        });
    }

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        fetchProposals(searchTerm);
    });

    // Carrega a lista inicial de propostas ao carregar a página
    fetchProposals();
});
