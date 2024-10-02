let workbook;
let tableData = [];
let selectedColumns = {
    'CPF': null,
    'NUMERO DA PROPOSTA': null,
    'CODIGO DA TABELA': null
};

// Carregar o arquivo XLSX ou CSV
document.getElementById('upload').addEventListener('change', function(event) {
    const reader = new FileReader();
    const file = event.target.files[0];

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        workbook = XLSX.read(data, { type: 'array' });

        populateSheetSelector(workbook.SheetNames);
    };

    reader.readAsArrayBuffer(file);
});

// Exibir a lista de planilhas disponíveis
function populateSheetSelector(sheetNames) {
    const selector = document.getElementById('sheet-selector');
    selector.innerHTML = '';

    sheetNames.forEach((name, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = name;
        selector.appendChild(option);
    });

    document.getElementById('sheet-selector-container').style.display = 'block';
    selector.addEventListener('change', () => displayTable(sheetNames[selector.value]));

    displayTable(sheetNames[0]);
}

// Exibir a tabela com os dados da planilha selecionada
function displayTable(sheetName) {
    const sheet = workbook.Sheets[sheetName];
    tableData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    const container = document.getElementById('table-container');
    container.innerHTML = '';

    const table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-hover', 'table-sm');

    const headerRow = document.createElement('tr');
    tableData[0].forEach((header, index) => {
        const th = document.createElement('th');
        th.classList.add('text-center');
        const select = document.createElement('select');
        select.classList.add('form-select', 'form-select-sm');
        select.innerHTML = `
            <option value="">Selecionar...</option>
            <option value="CPF">CPF</option>
            <option value="NUMERO DA PROPOSTA">NUMERO DA PROPOSTA</option>
            <option value="CODIGO DA TABELA">CODIGO DA TABELA</option>
        `;
        select.addEventListener('change', (e) => handleColumnSelection(e, index));
        th.appendChild(select);
        th.appendChild(document.createTextNode(header));
        headerRow.appendChild(th);
    });

    table.appendChild(headerRow);

    for (let i = 1; i < tableData.length; i++) {
        const row = document.createElement('tr');
        tableData[i].forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell || '';
            row.appendChild(td);
        });
        table.appendChild(row);
    }

    container.appendChild(table);

    const processButton = document.getElementById('process');
    if (processButton) {
        processButton.disabled = true;
    }
}

// Capturar a seleção de colunas
function handleColumnSelection(event, columnIndex) {
    const columnName = event.target.value;

    // Desmarcar a coluna anterior que tinha sido atribuída ao nome
    for (let key in selectedColumns) {
        if (selectedColumns[key] === columnIndex) {
            selectedColumns[key] = null;
        }
    }

    // Atribuir a nova coluna selecionada ao nome correto
    if (columnName !== '') {
        selectedColumns[columnName] = columnIndex;
    }

    // Ativar o botão de envio apenas se todas as colunas obrigatórias forem selecionadas
    const allColumnsSelected = Object.values(selectedColumns).every(index => index !== null);
    document.getElementById('process').disabled = !allColumnsSelected;
}

// Processar os dados
document.getElementById('process').addEventListener('click', function() {
    const selectedData = tableData.slice(1).map(row => {
        return {
            'CPF': row[selectedColumns['CPF']],
            'NUMERO DA PROPOSTA': row[selectedColumns['NUMERO DA PROPOSTA']],
            'CODIGO DA TABELA': row[selectedColumns['CODIGO DA TABELA']]
        };
    });

    const bankID = document.getElementById("bankSelect").value;
    const nameReport = document.getElementById("report_name").value;

    const dataToSend = {
        columns: selectedData,
        bankID,
        nameReport,
    };

    fetch('/process-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
    })
    .then(response => response.json())
    .then(data => {
        const notification = document.getElementById('notification');

        if (data.message) {
            notification.className = 'alert alert-success';
            notification.innerText = data.message;
            setTimeout(() => window.location.reload(), 3000);
            // Exibir dados inválidos, se existirem
            if (data.invalid_data.length > 0) {
                let invalidTable = '<h5>Dados Inválidos</h5><table class="table table-bordered"><thead><tr><th>CPF</th><th>Número da Proposta</th><th>Código da Tabela</th></tr></thead><tbody>';
                data.invalid_data.forEach(item => {
                    invalidTable += `<tr><td>${item.CPF}</td><td>${item["Numero da Proposta"]}</td><td>${item["Codigo da Tabela"]}</td></tr>`;
                });
                invalidTable += '</tbody></table>';
                document.getElementById('table-container').innerHTML += invalidTable;
            }
            setTimeout(() => window.location.reload(), 3000);
        } else {
            notification.className = 'alert alert-danger';
            notification.innerText = data.error || 'Erro ao processar os dados';
        }

        notification.style.display = 'block';
        setTimeout(() => { notification.style.display = 'none'; }, 3000);
    })
    .catch(error => {
        console.error('Erro ao enviar dados:', error);
        const notification = document.getElementById('notification');
        notification.className = 'alert alert-danger';
        notification.innerText = 'Ocorreu um erro ao processar os dados.';
        notification.style.display = 'block';
    });
});
