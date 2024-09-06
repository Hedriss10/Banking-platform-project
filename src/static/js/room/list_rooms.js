$(document).ready(function () {

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

    $('#association-form').submit(function (event) {
        event.preventDefault();

        let selectedVendors = [];
        let selectedRoom = null;

        $('.vendor-checkbox:checked').each(function () {
            selectedVendors.push($(this).val());
        });

        let checkedRooms = $('.room-checkbox:checked');
        if (checkedRooms.length > 1) {
            alert('Selecione apenas uma sala para associar.');
            return;
        } else if (checkedRooms.length === 1) {
            selectedRoom = checkedRooms.val();
        }

        if (selectedVendors.length === 0 || !selectedRoom) {
            alert('Selecione pelo menos um vendedor e uma sala.');
            return;
        }

        $.ajax({
            url: '/associate_vendors',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ roomId: selectedRoom, vendors: selectedVendors }),
            success: function (response) {
                alert(response.message);
                location.reload();
            },
            error: function (response) {
                alert('Erro: ' + response.responseJSON.error);
            }
        });
    });
});