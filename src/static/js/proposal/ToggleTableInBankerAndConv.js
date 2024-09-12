// document.addEventListener('DOMContentLoaded', function() {
//     const convenioSelect = document.getElementById('convenioSelectProposal');
//     const tableSelect = document.getElementById('tableSelectProposal');

//     convenioSelect.addEventListener('change', function() {
//         const selectedConvenioId = convenioSelect.value;
//         const tableOptions = tableSelect.querySelectorAll('.table-options');

//         tableOptions.forEach(option => {
//             if (option.getAttribute('data-convenio-id') === selectedConvenioId || selectedConvenioId === '') {
//                 option.style.display = 'block';
//             } else {
//                 option.style.display = 'none';
//             }
//         });
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    const convenioSelect = document.getElementById('convenioSelectProposal');
    const tableSelect = document.getElementById('tableSelectProposal');
    
    const tableOptions = Array.from(document.querySelectorAll('#tableSelectProposal option')).filter(option => option.value);

    convenioSelect.addEventListener('change', function() {
        const selectedConvenioId = this.value;

        tableSelect.disabled = !selectedConvenioId;

        tableSelect.innerHTML = '<option value="">Escolha...</option>';

        if (selectedConvenioId) {
            tableOptions.forEach(option => {
                if (option.dataset.convenioId === selectedConvenioId) {
                    const newOption = document.createElement('option');
                    newOption.value = option.value;
                    newOption.innerHTML = option.innerHTML;
                    tableSelect.appendChild(newOption);
                }
            });
        }
    });
});