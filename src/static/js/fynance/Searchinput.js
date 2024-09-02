document.getElementById('searchInput').addEventListener('input', function() {
  const searchTerm = this.value.toLowerCase();

  fetch(`/manage-comission?search=${searchTerm}`, {
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
      // Atualiza a tabela com os novos dados
      const tbody = document.querySelector('tbody');
      tbody.innerHTML = ''; // Limpa as linhas existentes

      data.forEach((bank, index) => {
          const row = document.createElement('tr');
          row.innerHTML = `
              <th scope="row">${index + 1}</th>
              <td>${bank.bank_name}</td>
              <td>${bank.agreement_name}</td>
              <td>${bank.table_name}</td>
              <td>${bank.table_code}</td>
              <td>${bank.rate}%</td>
          `;
          tbody.appendChild(row);
      });

      // Exibe mensagem se nenhum resultado for encontrado
      if (data.length === 0) {
          const emptyRow = document.createElement('tr');
          emptyRow.innerHTML = `
              <td colspan="6" class="text-center">Nenhuma comissão encontrada</td>
          `;
          tbody.appendChild(emptyRow);
      }
  })
  .catch(error => console.error('Erro ao buscar dados:', error));
});
