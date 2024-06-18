document.addEventListener('DOMContentLoaded', function() {
    const importForm = document.getElementById('importForm');

    importForm.addEventListener('submit', function(event) {
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

    bankSelect.addEventListener('change', function() {
        var selectedBankId = this.value;
        document.querySelectorAll('.convenio-options').forEach(option => {
            option.style.display = option.getAttribute('data-bank-id') === selected

    BankId ? 'block' : 'none';
            });
            convenioSelect.value = '';
        });
});
