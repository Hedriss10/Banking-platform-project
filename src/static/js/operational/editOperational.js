document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.img-thumbnail').forEach(function(img) {
      img.addEventListener('click', function() {
          const expandedImage = document.getElementById('expandedImage');
          expandedImage.src = this.src;

          const modal = new bootstrap.Modal(document.getElementById('imageModal'));
          modal.show();
      });
  });
});