function cpf(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.toString().length != 11 || /^(\d)\1{10}$/.test(cpf)) return false;
    var result = true;
    [9, 10].forEach(function(j) {
        var soma = 0, r;
        cpf.split(/(?=)/).splice(0, j).forEach(function(e, i) {
            soma += parseInt(e) * ((j + 2) - (i + 1));
        });
        r = soma % 11;
        r = (r < 2) ? 0 : 11 - r;
        if (r != cpf.substring(j, j + 1)) result = false;
    });
    return result;
}

document.addEventListener('DOMContentLoaded', function () {
    var proposalForm = document.getElementById('proposalForm');

    proposalForm.addEventListener('submit', function (event) {
        event.preventDefault();

        var cpfField = document.querySelector('input[name="CPF"]').value;

        if (!cpf(cpfField)) {
            alert('CPF inválido. Por favor, insira um CPF válido.');
            return;
        }

        var formData = new FormData(proposalForm);

        var fileFields = [
            'rg_cnh_completo',
            'rg_frente',
            'rg_verso',
            'contracheque',
            'extrato_consignacoes',
            'comprovante_residencia',
            'selfie',
            'comprovante_bancario',
            'detalhamento_inss',
            'historico_consignacoes_inss'
        ];

        fileFields.forEach(function(fieldName) {
            var files = document.querySelector(`input[name="${fieldName}"]`).files;
            if (files.length > 0) {
                for (var i = 0; i < files.length; i++) {
                    formData.append(fieldName, files[i]);
                }
            }
        });

        fetch('/proposal/new-proposal', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Contrato registrado com sucesso!');
                window.location.href = "/home";
            } else {
                alert(data.message || 'Erro ao registrar o contrato.');
            }
        })
        .catch(error => {
            console.error('Erro ao enviar o formulário:', error);
            alert('Erro ao enviar o formulário.');
        });
    });
});
