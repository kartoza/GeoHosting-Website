
function showCustomAlert(message, alertType, backgroundContainer) {
    try{
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
            backgroundContainer? backgroundContainer.classList.remove('blur'): ''; 
        });

        if(backgroundContainer)
            backgroundContainer.classList.add('blur');
    }catch(err){
        console.error(err);
    }
    
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

// responsible for providing updated urls
function updateUrl(replaceWith){
    var currentUrl = window.location.href;
    var firstSlashIndex = currentUrl.indexOf('/');
    var baseUrl = currentUrl.substring(0, firstSlashIndex + 1);
    return baseUrl + replaceWith;
}

function getCurrentPage() {
    return window.location.href.toLowerCase();
}

function navigateToForgotPassword() {
    window.location.href = updateUrl('account/forgot_password.html');
}

function navigateToSignIn() {
    window.location.href = updateUrl('account/sign_in.html');
}

function navigateToSignUp() {
    window.location.href = updateUrl('account/sign_up.html');
}

function navigateToSupport(){
  window.location.href = updateUrl('portal/support_tickets.html');
}

function navigateToNotifications(){
  window.location.href = updateUrl('portal/user_notifications.html');
}

function navigateToHostedServices(){
  window.location.href = updateUrl('portal/hosted_services.html');
}

function navigateToProducts(){
    window.location.href = updateUrl('main/products.html');
  }

function navigateToProfile(){
  window.location.href = updateUrl('portal/user_profile.html');
}

function navigateToInvoices(){
  window.location.href = updateUrl('portal/product_invoices.html');
}


async function refreshCSRFToken() {
    const response = await fetch('/api/method/geohosting.api.get_csrf_token');
    const data = await response.json();
    if (data && data.message.csrf_token) {
        document.cookie = `csrf_token=${data.message.csrf_token}; path=/`;
    }
}


async function fetchWithCSRF(url, options) {
    try {
        if (!options.headers) {
            options.headers = {};
        }

        let csrfToken = getCookie('csrf_token');

        if (!csrfToken) {
            await refreshCSRFToken();
            csrfToken = getCookie('csrf_token');
        }

        options.headers['X-Frappe-CSRF-Token'] = csrfToken;

        let response = await fetch(url, options);

        if (response.status === 400 || response.status === 403) {
            await refreshCSRFToken();
            csrfToken = getCookie('csrf_token');
            options.headers['X-Frappe-CSRF-Token'] = csrfToken;
            response = await fetch(url, options);
        }

        return response;

    } catch (error) {
        console.error('Error fetching with CSRF token:', error);
        throw error;
    }
}


function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}