function toggleConvenios(bankId, event) {
    event.stopPropagation();  // Impede que o evento clique se propague para elementos pai
    var element = document.getElementById('convenios-' + bankId);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

function toggleConveniosBankersTables(convenioId, event) {
    event.stopPropagation();
    var tablesList = document.getElementById('tables-' + convenioId);
    if (tablesList.style.display === 'none' || tablesList.style.display === '') {
        tablesList.style.display = 'block';
        // Inicializa a paginação para esta lista
        var controlsId = tablesList.getAttribute('data-controls-id');
        var controls = document.getElementById(controlsId);
        if (controls) {
            paginateList(tablesList, controls, 10);
        }
    } else {
        tablesList.style.display = 'none';
        // Limpa os controles de paginação, se necessário
        var controlsId = tablesList.getAttribute('data-controls-id');
        var controls = document.getElementById(controlsId);
        if (controls) {
            controls.innerHTML = '';
        }
    }
}

function deleteTable(tableId) {
    event.stopPropagation(); 
    console.log('Deletar tabela', tableId);
}
function paginateList(list, controls, itemsPerPage) {
    var items = list.querySelectorAll('li.list-group-item:not(:first-child)');
    var pageCount = Math.ceil(items.length / itemsPerPage);
    var currentPage = 1;

    function showPage(page) {
        currentPage = page;
        var start = (currentPage - 1) * itemsPerPage;
        var end = start + itemsPerPage;

        for (var i = 0; i < items.length; i++) {
            items[i].style.display = (i >= start && i < end) ? 'list-item' : 'none';
        }
        renderControls();
    }

    function renderControls() {
        controls.innerHTML = '';
        for (var i = 1; i <= pageCount; i++) {
            var btn = document.createElement('button');
            btn.textContent = i;
            btn.className = 'btn btn-sm ' + (i === currentPage ? 'btn-primary' : 'btn-secondary');
            btn.addEventListener('click', function() {
                showPage(parseInt(this.textContent));
            });
            controls.appendChild(btn);
        }
    }

    if (items.length > 0) {
        showPage(1);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Remover a inicialização automática da paginação aqui
});
