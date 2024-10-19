document.addEventListener('DOMContentLoaded', function() {
  const modalElement = document.getElementById('imageModal');
  if (modalElement) {
    document.querySelectorAll('.img-thumbnail').forEach(function(img) {
        img.addEventListener('click', function() {
            const expandedImage = document.getElementById('expandedImage');
            if (expandedImage) { 
                expandedImage.src = this.src; 

                const modal = new bootstrap.Modal(modalElement);
                modal.show(); 
            } else {
                console.error("Elemento expandedImage não encontrado.");
            }
        });
    });
  } else {
    console.error("Elemento imageModal não encontrado.");
  }
});
