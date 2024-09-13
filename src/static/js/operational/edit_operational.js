document.addEventListener('DOMContentLoaded', function() {
    // Adiciona o evento de duplo clique para todas as imagens
    document.querySelectorAll('img.img-thumbnail').forEach(function(img) {
      img.addEventListener('dblclick', function() {
        const expandedImage = document.getElementById('expandedImage');
        expandedImage.src = this.src;  // Define a imagem do modal com a mesma do clique

        // Exibe o modal
        const modal = new bootstrap.Modal(document.getElementById('imageModal'));
        modal.show();
      });
    });
  });