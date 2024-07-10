document.addEventListener('DOMContentLoaded', function() {
    var bankerSelect = document.getElementById('bankerProposal');
    var convenioSelect = document.getElementById('convenioSelectProposal');
    var tableSelect = document.getElementById('tableSelectProposal');

    function hideOptions(options) {
        options.forEach(option => {
            option.style.display = 'none';
        });
    }

    function showRelevantOptions(options, container, relevantId, dataAttribute) {
        container.innerHTML = '<option value="">Escolha...</option>'; 
        options.forEach(option => {
            if (option.dataset[dataAttribute] === relevantId) {
                option.style.display = 'block'; 
                container.appendChild(option.cloneNode(true)); 
            }
        });
    }

    bankerSelect.addEventListener('change', function() {
        var selectedBankId = this.value;

        hideOptions([...document.querySelectorAll('.convenio-options'), ...document.querySelectorAll('.table-options')]);
        
        showRelevantOptions(document.querySelectorAll('.convenio-options'), convenioSelect, selectedBankId, 'bankId');

        convenioSelect.value = '';
        tableSelect.value = '';
    });

    convenioSelect.addEventListener('change', function() {
        var selectedConvenioId = this.value;

        hideOptions(document.querySelectorAll('.table-options'));

        showRelevantOptions(document.querySelectorAll('.table-options'), tableSelect, selectedConvenioId, 'convenioId');

        tableSelect.value = '';
    });
});
