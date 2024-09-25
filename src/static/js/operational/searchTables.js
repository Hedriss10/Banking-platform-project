document.getElementById('tableSearchInput').addEventListener('input', function() {
    const query = this.value;
    if (query.length > 2) { 
        fetch(`/search-tables?query=${query}`)
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('tableSelectProposal');
                select.innerHTML = ''; 
                data.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table.id;
                    option.text = `Tabela: ${table.name} - Tipo: ${table.type_table} - Código: ${table.code} - Prazo Inicio: ${table.start_term} - Prazo Fim ${table.end_term} - Comissão: ${table.rate}`;
                    select.appendChild(option);
                });
                select.disabled = false;
            });
    }
});