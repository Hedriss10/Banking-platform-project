document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
  
    fetch(`/proposal?search=${searchTerm}`, {
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
        tbody.innerHTML = '';
  
        data.forEach((bank, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${ index }</td>
                <td>${bank.bank_name}</td>
                <td>${bank.agreement_name}</td>
                <td>${bank.table_name}</td>
                <td>${bank.table_code}</td>
            `;
            tbody.appendChild(row);
        });

        if (data.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="5" class="text-center">Nenhuma comissão encontrada</td>
            `;
            tbody.appendChild(emptyRow);
        }
    })
    .catch(error => console.error('Erro ao buscar dados:', error));
  });
  