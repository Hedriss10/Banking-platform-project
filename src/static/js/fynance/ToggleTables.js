function toggleConvenios(bankId, event) {
    event.stopPropagation();  // Impede que o evento clique se propague para elementos pai
    var element = document.getElementById('convenios-' + bankId);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

function toggleConveniosBankersTables(tablesId, event) {
    event.stopPropagation();  // Impede que o evento clique se propague para elementos pai
    var element = document.getElementById('tables-' + tablesId);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

function deleteTable(tableId) {
    event.stopPropagation();  // Impede que o evento clique se propague para elementos pai
    // Implemente a lógica para deletar a tabela aqui
    console.log('Deletar tabela', tableId);
}
