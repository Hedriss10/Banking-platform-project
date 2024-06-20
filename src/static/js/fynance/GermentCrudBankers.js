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

function registerConvenio() {
    const convName = document.getElementById('convName').value;
    const bankId = document.getElementById('bankerId').value; 

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
        } else {
            alert(data.error || 'Error occurred while adding the convenio.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while communicating with the server.');
    });
}

function deleteBanker() {
    const selectElement = document.getElementById('bankerIdDelete');
    const bankId = selectElement.value; 

    if (!bankId) {
        alert('O ID do banco é necessário para deletar.');
        return;
    }

    const url = `/delete-bankers/${bankId}`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message || 'Banco deletado com sucesso.');

            // Remove a opção correspondente ao ID do banco deletado
            const optionToRemove = selectElement.querySelector(`option[value="${bankId}"]`);
            if (optionToRemove) {
                selectElement.removeChild(optionToRemove);
            }
        } else {
            alert(data.error || 'Ocorreu um erro ao deletar o banco.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocorreu um erro ao comunicar com o servidor.');
    });
}

// Adicionando ouvintes de eventos para os formulários
document.getElementById('addBankForm').addEventListener('submit', function(event) {
    event.preventDefault();
    registerBank();
});

document.getElementById('addConvenioForm').addEventListener('submit', function(event) {
    event.preventDefault();
    registerConvenio();
});


document.getElementById('deleteBankForm').addEventListener('submit', function(event) {
    event.preventDefault();
    deleteBanker();
});
