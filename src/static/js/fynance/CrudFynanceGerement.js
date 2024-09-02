// Função genérica para deletar recursos
function deleteResource(url, id, successCallback) {
    if (!id) {
        alert('Um ID é necessário para deletar.');
        return;
    }

    fetch(url, {
        method: 'POST',  // Considere mudar para 'DELETE' se for apropriado para a sua API
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                successCallback();
                alert(data.message || 'Deletado com sucesso!');
            } else {
                alert(data.error || 'Ocorreu um erro ao deletar.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocorreu um erro ao comunicar com o servidor.');
        });
}

// Função para deletar uma tabela específica
function deleteTable(tableId, event) {
    event.stopPropagation();
    const url = `/delete-bankers/tables/${tableId}`;
    if (confirm('Tem certeza que deseja deletar esta tabela?')) {
        deleteResource(url, tableId, () => {
            document.querySelector(`[data-id="${tableId}"]`).parentElement.remove();
        });
    }
}

// Especificação para deletar um banqueiro
function deleteBanker(bankId) {
    const url = `/delete-bankers/${bankId}`;
    deleteResource(url, bankId, () => {
        const selectElement = document.getElementById('bankerId');
        const optionToRemove = selectElement.querySelector(`option[value="${bankId}"]`);
        if (optionToRemove) {
            selectElement.removeChild(optionToRemove);
        }
    });
}

// Especificação para deletar um convênio
function deleteConvenio(event, element) {
    event.stopPropagation();
    const convenioId = element.getAttribute('data-id');
    const url = `/delete-bankers/conv/${convenioId}`;
    if (confirm('Tem certeza que deseja deletar este convênio?')) {
        deleteResource(url, convenioId, () => {
            element.parentElement.remove();
            window.location.reload();
        });
    }
}

// Especificação para deletar uma tabela em um convênio
function deleteTableInCovInBanker(event, element) {
    event.stopPropagation();
    const tableId = element.getAttribute('data-id');
    const url = `/delete-bankers/conv/tables/${tableId}`;
    if (confirm('Tem certeza que deseja deletar esta tabela?')) {
        deleteResource(url, tableId, () => {
            element.parentElement.remove();
        });
    }
}
// Especificação para cadastrar um banco 
function registerBank() {
    const bankName = document.getElementById('bankName').value;

    fetch('/register-bankers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: bankName })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Banco cadastrado com sucesso.');
                window.location.reload();
            } else {
                alert(data.error || 'Error occurred while adding the bank.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while communicating with the server.');
        });
}

// Especificação para cadastrar um convenio
function registerConvenio() {
    const convName = document.getElementById('convName').value;
    const bankId = document.getElementById('bankerIdConv').value;

    var data = {
        name: convName,
        bank_id: bankId
    };

    fetch('/register-convenio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Convênio cadastrado com sucesso.');
                window.location.reload();
            } else {
                alert(data.error || 'Error occurred while adding the convenio.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while communicating with the server.');
        });
}

// Especificação para importar a tabela
// Função para registrar as tabelas importadas
function registerTables() {
    const importForm = document.getElementById('importForm');
    importForm.addEventListener('submit', function (event) {
        event.preventDefault();

        var fileInput = document.getElementById('fileInput');
        var bankSelect = document.getElementById('bankSelect');
        var convenioSelect = document.getElementById('convenioSelect');

        if (!fileInput.files.length) {
            alert('Por favor, selecione um arquivo para importar.');
            return;
        }

        var formData = new FormData(this);
        formData.append('bankId', bankSelect.value);
        formData.append('convenioId', convenioSelect.value);

        fetch('/register-bankers/tables', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            
            const notification = document.getElementById('notificationImportBanker');
            if (data.message === "Dados processados com sucesso!") {
                notification.className = 'alert alert-success';
                notification.innerText = data.message;
                setTimeout(() => { window.location.reload(); }, 2000)
            
            } else {
                alert('Erro ao importar dados: ' + data.error);
            }
        })
        .catch(error => {
            // console.error('Error:', error);
            alert('Tabela importada com sucesso!');
            window.location.reload(); // atualizar e força a refazer o get no banco
        });
    });

    // Atualiza opções de convênio com base no banco selecionado
    bankSelect.addEventListener('change', function () {
        var selectedBankId = this.value;
        document.querySelectorAll('.convenio-options').forEach(option => {
            option.style.display = option.getAttribute('data-bank-id') === selectedBankId ? 'block' : 'none';
        });
        convenioSelect.value = '';
    });
}

function setupImportForm() {
    const importForm = document.getElementById('importFormTableOne');

    if (!importForm) return; // Sai da função se o formulário não existir na página

    const bankSelect = document.getElementById('bankSelectOneTable');
    const convenioSelect = document.getElementById('convenioSelectOne');

    // Função para atualizar as opções de convênio baseadas no banco selecionado
    function updateConvenioOptions(selectedBankId) {
        const convenioOptions = document.querySelectorAll('.convenio-options-onetables');
        convenioOptions.forEach(option => {
            option.style.display = option.getAttribute('data-bank-id') === selectedBankId ? 'block' : 'none';
        });
    }

    // Adiciona evento de mudança ao seletor de bancos
    bankSelect.addEventListener('change', function() {
        updateConvenioOptions(this.value);
        convenioSelect.value = '';  // Limpa a seleção de convênios ao mudar o banco
    });

    // Atualiza as opções de convênio ao carregar a página se já existir um banco selecionado
    if (bankSelect.value) {
        updateConvenioOptions(bankSelect.value);
    }

    // Manipulação do evento de submissão do formulário para importação de tabela
    importForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        formData.append('bankId', bankSelect.value);
        formData.append('convenioId', convenioSelect.value);

        fetch('/register-bankers/tables/banker/conv/one', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Arquivo importado com sucesso!');
                window.location.reload();  // Considerar atualizar dinamicamente sem recarregar
            } else {
                alert('Erro ao importar dados: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao comunicar com o servidor: ' + error.message);
        });
    });
}


// Evento para submissão do formulário de deleção de banqueiro
document.getElementById('deleteBanker').addEventListener('submit', function (event) {
    event.preventDefault();
    const bankId = document.getElementById('bankerId').value;
    deleteBanker(bankId);
});

// Adicionando ouvintes de eventos para os formulários para cadastrar um banco
document.getElementById('addBankForm').addEventListener('submit', function (event) {
    event.preventDefault();
    registerBank();
});

// Adcionando ouvintes de eventos para os formularios para cadastrar um convenio 
document.getElementById('addBankConvForm').addEventListener('submit', function (event) {
    event.preventDefault();
    registerConvenio();
});

// Inicia a função registerTables ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    registerTables();
});


// Adiciona o listener diretamente no ID específico ao carregar a página
document.addEventListener('DOMContentLoaded', setupImportForm);

