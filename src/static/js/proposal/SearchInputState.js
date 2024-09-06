document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();

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
                <td colspan="6" class="text-center">Nenhuma proposta encontrada</td>
            `;
            tbody.appendChild(emptyRow);
            return;
        }

        data.forEach((p, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${p.name_and_lastname}</td>
                <td>${p.created_at}</td>
                <td>
                    ${p.active ? '<span class="badge bg-success">Aprovado</span>' : ''}
                    ${p.block ? '<span class="badge bg-danger">Recusado</span>' : ''}
                    ${p.is_status ? '<span class="badge bg-warning">Em Andamento</span>' : ''}
                    ${!p.active && !p.block && !p.is_status ? '<span class="badge bg-secondary">Pendente</span>' : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => console.error('Erro ao buscar dados:', error));
});
