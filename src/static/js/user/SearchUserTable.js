document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('tbody tr');

    rows.forEach(row => {
      const rowData = row.textContent.toLowerCase();
      if (searchTerm === '') {
        row.style.display = ''; // Mostra todas as linhas se o campo de busca estiver vazio
      } else if (rowData.includes(searchTerm)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });