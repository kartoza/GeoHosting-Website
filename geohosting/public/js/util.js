
function showCustomAlert(message, alertType, backgroundContainer) {
    var customAlert = document.createElement('div');
    customAlert.classList.add('alert', alertType);
    customAlert.innerHTML = `
        <h4>${message}</h4>
        <a class="close">&times;</a>
    `;

    document.body.appendChild(customAlert);

    $(".close").click(function() {
    $(this)
        .parent(".alert")
        .fadeOut();
        backgroundContainer.classList.remove('blur'); 
    });

    backgroundContainer.classList.add('blur');
}