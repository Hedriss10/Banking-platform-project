document.addEventListener('DOMContentLoaded', function() {
    const bankSelect = document.getElementById('bankSelectOneTable');
    const convenioSelect = document.getElementById('convenioSelectOne');
    const importForm = document.getElementById('importFormTableOne');

    function updateConvenioOptions(selectedBankId) {
        const convenioOptions = document.querySelectorAll('.convenio-options-onetables');
        convenioOptions.forEach(option => {
            if (option.getAttribute('data-bank-id') === selectedBankId) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none'; 
            }
        });
    }

    bankSelect.addEventListener('change', function() {
        updateConvenioOptions(this.value);
        convenioSelect.value = ''; 
    });

    if (bankSelect.value) {
        updateConvenioOptions(bankSelect.value);
    }

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
                window.location.reload();
            } else {
                alert('Erro ao importar dados: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao comunicar com o servidor: ' + error.message);
        });
    });
});
