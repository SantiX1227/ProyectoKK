// static/js/usuario.js

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector(".file-dropzone input[type='file']");
  const fileLabel = document.getElementById("file-name");

  if (fileInput && fileLabel) {
    fileInput.addEventListener("change", (event) => {
      const files = event.target.files;
      if (files && files.length > 0) {
        fileLabel.textContent = `Archivo: ${files[0].name}`;
        fileLabel.style.fontWeight = "600";
        fileLabel.style.color = "var(--text-main)";
      } else {
        fileLabel.textContent = "PNG, JPG hasta 5MB";
        fileLabel.style.fontWeight = "normal";
        fileLabel.style.color = "var(--text-muted)";
      }
    });
  }
});