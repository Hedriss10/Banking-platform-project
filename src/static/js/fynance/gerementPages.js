// Função para alternar a seleção de todas as checkboxes em um convênio
function toggleSelectAll(convenioId, event) {
    event.stopPropagation();

    const checkboxes = document.querySelectorAll(`#tables-${convenioId} .table-checkbox`);
    const selectAllCheckbox = document.getElementById(`select-all-${convenioId}`);
    checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
}

// Função para alternar a exibição dos convênios sob um banco
function toggleConvenios(bankId, event) {
    event.stopPropagation();  // Impede que o evento clique se propague para elementos pai
    var element = document.getElementById('convenios-' + bankId);
    if (element.style.display === 'none' || element.style.display === '') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

// Função para alternar a exibição das tabelas sob um convênio e inicializar o campo de busca
function toggleConveniosBankersTables(convenioId, event) {
    event.stopPropagation(); // Evita a propagação do clique para outros elementos

    var tablesList = document.getElementById('tables-' + convenioId);
    var searchInput = document.getElementById('tableSearchInput-' + convenioId);

    if (tablesList.style.display === 'none' || tablesList.style.display === '') {
        tablesList.style.display = 'block'; // Exibe as tabelas ao clicar
        searchInput.style.display = 'block'; // Exibe o campo de busca
    } else {
        tablesList.style.display = 'none'; // Oculta as tabelas
        searchInput.style.display = 'none'; // Oculta o campo de busca
    }
}

// Event listener para o evento 'change' do 'bankSelect'
var bankSelect = document.getElementById('bankSelect');
if (bankSelect) {
    bankSelect.addEventListener('change', function() {
        var selectedBankId = this.value;
        var convenioOptions = document.querySelectorAll('.convenio-options');

        convenioOptions.forEach(function(option) {
            option.style.display = 'none';
        });

        convenioOptions.forEach(function(option) {
            if (option.getAttribute('data-bank-id') === selectedBankId) {
                option.style.display = 'block';
            }
        });

        document.getElementById('convenioSelect').value = '';
    });
}

// Função para deletar uma tabela (implemente a lógica conforme necessário)
function deleteTable(tableId, event) {
    event.stopPropagation(); 
    console.log('Deletar tabela', tableId);
    // Implemente a lógica de deleção aqui
}

// Função para alternar a exibição das tabelas (se necessário)
function toggleTables(convenioId) {
    var element = document.getElementById("tables-" + convenioId);
    var isVisible = element.style.display !== "none";
    element.style.display = isVisible ? "none" : "block";
}

// Função para filtrar as tabelas pelo código da tabela
function filterTables(convenioId) {
    // Obtém o valor do input de busca e converte para maiúsculas
    var input = document.getElementById('tableSearchInput-' + convenioId);
    var filter = input.value.toUpperCase();

    // Seleciona todas as tabelas associadas ao convênio específico
    var tables = document.querySelectorAll('#tables-' + convenioId + ' .table-item');

    // Itera sobre todas as tabelas e exibe apenas as que correspondem ao código da tabela
    tables.forEach(function(tableItem) {
        var tableCode = tableItem.getAttribute('data-table-code').toUpperCase();

        // Verifica se o código da tabela contém o valor digitado no input
        if (tableCode.indexOf(filter) > -1) {
            tableItem.style.display = ''; // Exibe a tabela que corresponde
        } else {
            tableItem.style.display = 'none'; // Oculta as que não correspondem
        }
    });
}