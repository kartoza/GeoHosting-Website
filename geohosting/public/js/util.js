
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


async function fetchUserInfo() {
    try {
        const response = await fetch('/api/method/geohosting.api.get_user_info', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user info');
        }

        const data = await response.json();
        return data.message;
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}