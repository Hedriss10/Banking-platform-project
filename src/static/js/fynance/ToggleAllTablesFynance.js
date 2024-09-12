function toggleSelectAll(convenioId, event) {
    event.stopPropagation();

    const checkboxes = document.querySelectorAll(`#tables-${convenioId} .table-checkbox`);
    const selectAllCheckbox = document.getElementById(`select-all-${convenioId}`);
    checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
}

function toggleConvenios(bankId, event) {
    if (event.target.tagName === 'INPUT') return;

    const convenioList = document.getElementById(`convenios-${bankId}`);
    convenioList.style.display = convenioList.style.display === 'none' ? 'block' : 'none';
}

function toggleConveniosBankersTables(convenioId, event) {
    if (event.target.tagName === 'INPUT') return;

    const tableList = document.getElementById(`tables-${convenioId}`);
    tableList.style.display = tableList.style.display === 'none' ? 'block' : 'none';
}