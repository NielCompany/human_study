document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("file-input");
    const preview = document.getElementById("preview");
    const fileName = document.getElementById("file-name");
  
    fileInput.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (file) {
        fileName.textContent = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          preview.src = e.target.result;
          preview.style.display = "block";
        };
        reader.readAsDataURL(file);
      } else {
        fileName.textContent = "선택된 파일 없음";
        preview.style.display = "none";
      }
    });
  });
  