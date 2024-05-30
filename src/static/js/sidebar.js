$(document).ready(function() {
    // Manipulação de cliques em links que não usam HTMX
    $(".sidebar ul li a:not([hx-get])").on('click', function (event) {
        event.preventDefault();  // Previne a navegação padrão
        var target = $(this).data('target'); // Pega o seletor do conteúdo a ser mostrado
        $('.content-section').hide(); // Oculta todas as seções de conteúdo
        $(target).show(); // Mostra apenas a seção relevante

        // Atualiza a classe 'active' para o item da lista clicado
        $(".sidebar ul li.active").removeClass('active');
        $(this).parent().addClass('active');
    });

    // Manipulação de cliques em links que usam HTMX
    $(".sidebar ul li a[hx-get]").on('click', function () {
        // Apenas atualiza a classe 'active', HTMX cuidará de carregar e exibir o conteúdo
        $(".sidebar ul li.active").removeClass('active');
        $(this).parent().addClass('active');
    });

    // Botão para abrir a sidebar em telas menores
    $('.open-btn').on('click', function () {
        $('.sidebar').addClass('active');
    });

    // Botão para fechar a sidebar em telas menores
    $('.close-btn').on('click', function () {
        $('.sidebar').removeClass('active');
    });

    // Eventos HTMX para diagnóstico e ajustes adicionais
    document.body.addEventListener('htmx:beforeSwap', function(event) {
        console.log('HTMX está prestes a trocar conteúdo...');
    });

    document.body.addEventListener('htmx:afterSwap', function(event) {
        console.log('HTMX trocou conteúdo.');
        // Aqui você pode inserir qualquer lógica adicional que precise ser executada após o HTMX atualizar o conteúdo
    });
});
