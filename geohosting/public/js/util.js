var proceedToCheckout = true;

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

function insertLineBreakIfNeeded(text) {
    const maxLength = 29;

    if (text.length <= maxLength) {
        return text;
    }

    // Split the text into words
    const words = text.split(' ');

    // Reconstruct the text with words, inserting <br> where needed
    let line1 = '';
    let line2 = '';

    for (let word of words) {
        if ((line1 + ' ' + word).length <= maxLength) {
            line1 += (line1 === '' ? '' : ' ') + word;
        } else {
            line2 += (line2 === '' ? '' : ' ') + word;
        }
    }

    return line1 + '<br>' + line2;
}

// TODO: for future usage it is better to fetch images for each product in erpnext when product is clicked
async function fetchAttachments(item_code) {
    const attachmentsUrl = `/api/resource/File`;
    const filters = [
        ["attached_to_doctype", "=", "Item"],
        ["attached_to_name", "=", item_code]
    ];
    const params = new URLSearchParams({
        'filters': JSON.stringify(filters),
        'fields': JSON.stringify(["*"]) 
    });

    try {
        const response = await fetch(`${attachmentsUrl}?${params}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch attachments: ${response.statusText}`);
        }
        const attachmentsData = await response.json();
        const screenshotAttachment = attachmentsData.data.find(file => file.file_name.endsWith("screenshot.png"));

        return screenshotAttachment.file_url;
    } catch (error) {
        console.error("Error fetching attachments:", error);
    }
}


function formatCurrencyDisabled(value, currency) {
    let isInteger = Number.isInteger(value);
    let options = {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: isInteger ? 0 : 2,
        maximumFractionDigits: isInteger ? 0 : 2
    };
    
    // Format the value using toLocaleString
    let formattedValue = value.toLocaleString('en-ZA', options);
    if (!isInteger && number >= 100000) {
        let parts = formattedValue.split('.');
        let main = parts[0];
        let decimals = parts.length > 1 ? '.' + parts[1] : '';
        formattedValue = `${main}<br>${decimals}`;
    } else if (number >= 1000000) {
        let parts = formattedValue.split('.');
        let main = parts[0];
        let decimals = parts.length > 1 ? '.' + parts[1] : '';
        formattedValue = `${main}<br>${decimals}`;
    }
}


function proceedToCheckout(){
    return true;
}