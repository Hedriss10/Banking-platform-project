$(document).ready(function () {
    // Inicializa as tabelas com DataTables
    $('#vendor-table').DataTable({
        paging: true,
        pageLength: 10,
        lengthChange: false,
        searching: true,
        ordering: true,
        info: false,
        autoWidth: false,
        language: {
            search: "Buscar:",
            paginate: {
                next: "Próximo",
                previous: "Anterior"
            }
        }
    });

    $('#room-table').DataTable({
        paging: false,
        searching: false,
        ordering: false,
        info: false,
        autoWidth: false
    });

    // Carrega as seleções salvas do localStorage ao carregar a página
    loadSelections();

    // Evento de seleção de vendedores
    $('.vendor-checkbox').on('change', function () {
        saveSelectedVendors();  // Salva as seleções ao alterar
    });

    // Evento de seleção de sala
    $('.room-checkbox').on('change', function () {
        saveSelectedRoom();  // Salva a seleção da sala ao alterar
    });

    // Envio do formulário para associar vendedores à sala
    $('#association-form').submit(function (event) {
        event.preventDefault();  // Impede o comportamento padrão de envio do formulário

        let selectedVendors = JSON.parse(localStorage.getItem('selectedVendors')) || [];
        let selectedRoom = localStorage.getItem('selectedRoom');

        if (selectedVendors.length === 0 || !selectedRoom) {
            alert('Selecione pelo menos um vendedor e uma sala.');
            return;
        }

        // Envio da requisição via AJAX
        $.ajax({
            url: '/associate_vendors',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ roomId: selectedRoom, vendors: selectedVendors }),
            success: function (response) {
                alert(response.message);
                localStorage.clear();  // Limpa as seleções ao completar a associação
                location.reload();  // Atualiza a página após sucesso
            },
            error: function (response) {
                alert('Erro: ' + response.responseJSON.error);
            }
        });
    });



    // Função para salvar vendedores selecionados no localStorage
    function saveSelectedVendors() {
        let selectedVendors = [];
        $('.vendor-checkbox:checked').each(function () {
            selectedVendors.push($(this).val());
        });
        localStorage.setItem('selectedVendors', JSON.stringify(selectedVendors));
    }

    // Função para salvar a sala selecionada no localStorage
    function saveSelectedRoom() {
        let selectedRoom = $('.room-checkbox:checked').val();
        if (selectedRoom) {
            localStorage.setItem('selectedRoom', selectedRoom);
        }
    }

    // Função para carregar as seleções salvas do localStorage
    function loadSelections() {
        let selectedVendors = JSON.parse(localStorage.getItem('selectedVendors')) || [];
        let selectedRoom = localStorage.getItem('selectedRoom');

        // Marca os checkboxes dos vendedores já selecionados
        selectedVendors.forEach(function (vendorId) {
            $('.vendor-checkbox[value="' + vendorId + '"]').prop('checked', true);
        });

        // Marca o radio button da sala já selecionada
        if (selectedRoom) {
            $('.room-checkbox[value="' + selectedRoom + '"]').prop('checked', true);
        }
    }
});
