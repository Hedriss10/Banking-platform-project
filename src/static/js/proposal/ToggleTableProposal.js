document.getElementById('convenioSelectProposal').addEventListener('change', function() {
    var selectedConvenioId = this.value;
    var selectedBankId = document.getElementById('bankerProposal').value;

    var tableOptions = document.querySelectorAll('.table-options'); 

    tableOptions.forEach(function(option) {
        option.style.display = 'none';
    });

    Array.from(tableOptions).filter(function(option) {
        return option.getAttribute('data-convenio-id') === selectedConvenioId;
    }).forEach(function(option) {
        option.style.display = 'block';
    });

    document.getElementById('tableSelectProposal').value = '';
});
