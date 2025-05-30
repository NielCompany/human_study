document.addEventListener("DOMContentLoaded", function () {
    const msg = document.getElementById("flash-message");
    if (msg && msg.innerText.trim() !== "") {
        alert(msg.innerText);  // SweetAlert 등으로 교체 가능
    }
});