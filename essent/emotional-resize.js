document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.emotional-section').forEach(function (section) {
    const text = section.querySelector('.emotional-text-content');
    const img  = section.querySelector('.emotional-img-wrapper img');
    if (!text || !img) return;

    const textHeight = text.getBoundingClientRect().height;
    img.style.maxHeight = textHeight + 'px';
  });
});
