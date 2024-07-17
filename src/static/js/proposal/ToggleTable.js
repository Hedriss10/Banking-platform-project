document.getElementById('bankerProposal').addEventListener('change', function() {
    var selectedBankId = this.value;
    var convenioOptions = document.querySelectorAll('.convenio-options');

    convenioOptions.forEach(function(option) {
        option.style.display = 'none';
    });

    Array.from(convenioOptions).filter(function(option) {
        return option.getAttribute('data-bank-id') === selectedBankId;
    }).forEach(function(option) {
        option.style.display = 'block';
    });

    document.getElementById('convenioSelectProposal').value = '';
});
