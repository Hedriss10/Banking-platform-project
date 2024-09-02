let workbook;
let tableData = [];
let selectedColumns = [];

document.getElementById('upload').addEventListener('change', handleFile);

function handleFile(event) {
    const reader = new FileReader();
    const file = event.target.files[0];

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        workbook = XLSX.read(data, { type: 'array' });

        populateSheetSelector(workbook.SheetNames);
    };

    reader.readAsArrayBuffer(file);
}

function populateSheetSelector(sheetNames) {
    const selector = document.getElementById('sheet-selector');
    selector.innerHTML = '';

    sheetNames.forEach((name, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = name;
        selector.appendChild(option);
    });

    selector.style.display = 'block';
    selector.addEventListener('change', () => displayTable(sheetNames[selector.value]));

    displayTable(sheetNames[0]);
}

function displayTable(sheetName) {
    const sheet = workbook.Sheets[sheetName];
    tableData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    const container = document.getElementById('table-container');
    container.innerHTML = '';

    const table = document.createElement('table');
    const headerRow = document.createElement('tr');

    tableData[0].forEach((header, index) => {
        const th = document.createElement('th');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = index;
        checkbox.addEventListener('change', (e) => handleColumnSelection(e, index));
        th.appendChild(checkbox);
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
    document.getElementById('process').disabled = false;
}

function handleColumnSelection(event, columnIndex) {
    if (event.target.checked) {
        selectedColumns.push(columnIndex);
    } else {
        selectedColumns = selectedColumns.filter(col => col !== columnIndex);
    }
}

document.getElementById('process').addEventListener('click', () => {
    const selectedData = tableData.map(row => selectedColumns.map(colIndex => row[colIndex]));
    const bankID = document.getElementById("bankSelect").value;
    const convID = document.getElementById("convenioSelect").value;

    const dataToSend = {
        columns: selectedData,
        bankID,
        convID
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
            if (data.message ===  "Dados processados com sucesso!") {
                notification.className = 'alert alert-success';
                notification.innerText = data.message;
                setTimeout(() => { window.location.reload(); }, 2000);
            
            } else {
                notification.className = 'alert alert-danger';
                notification.innerText = data.error || 'Estou aqui';
            }

            notification.style.display = 'block';
            setTimeout(() => { notification.style.display = 'none'; }, 3000);
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
        });
});