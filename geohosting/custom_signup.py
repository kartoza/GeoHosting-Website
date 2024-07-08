import frappe
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def custom_signup(email, full_name, redirect_to):
    if frappe.db.exists("User", email):
        return {'status': 'error', 'message': 'User already exists'}
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "enabled": 1,
        "new_password": frappe.generate_hash(length=10)
    })
    user.append("roles", {
        "role": "Customer"
    })
    try:
        user.flags.ignore_permissions = True
        user.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(message=str(e), title="User Signup Error")
        return {'status': 'error', 'message': str(e)}

    send_welcome_email(user)

    return {'status': 'success', 'redirect_to': redirect_to}


def send_welcome_email(user):
    """Send a customised email welcome to new users from geoHosting."""

    subject = "Welcome to GeoHosting"
    message = f"""
        <div style="font-family: Roboto; color: #333;">
            <h1>Welcome to GeoHosting</h1>
            <p>Hello {user.first_name},</p>
            <p>A new account has been created for you at <a href="{frappe.utils.get_url()}">
            {frappe.utils.get_url()}</a>.</p>
            <p>Your login id is: {user.email}</p>
            <p>Click on the link below to complete your registration and set a new password.</p>
            <a href="{frappe.utils.get_url()}/update-password?key={get_password_reset_key(user)}" 
            style="display: inline-block; padding: 10px 20px; 
            background-color: #F4B340; color: #fff; 
            text-decoration: none; border-radius: 5px;">Complete Registration</a>
            <p>You can also copy-paste the following link in your browser:</p>
            <p><a href="{frappe.utils.get_url()}/update-password?key={get_password_reset_key(user)}">
            {frappe.utils.get_url()}/update-password?key={get_password_reset_key(user)}</a></p>
            <div style="margin-top: 30px; font-size: 0.8em; color: #666;">
            <p>Kartoza (Pty) Ltd.</p>
            <p>Company no: 2014/109067/07</p>
            <p>VAT Number: 4450266806</p>
            <p>Executive Directors: Tim Sutton MA; 
            Gavin Fleming MSc PrGISc [PGP1234] Non-Executive 
            Directors: Lawrence Hyslop M.Sc, MBA, PR Eng; Jenny Sutton MBA, LLM. Registered 
            Office: 28 Olienhout Street, Vermont, 7201, South Africa.</p>
            <p>Staff in South Africa (Gauteng, Western Cape, kwaZulu-Natal), Portugal, Indonesia and Tanzania</p>
            <p>Tel: +27 (0)73 768 8108 / +27 (0)87 809 2702</p>
                <p>Web: <a href="https://kartoza.com">https://kartoza.com</a> 
                Email: <a href="mailto:info@kartoza.com">info@kartoza.com</a></p>
                <p>Sent via ERPNext</p>
            </div>
        </div>
        """

    frappe.sendmail(recipients=user.email, subject=subject, message=message)


def get_password_reset_key(user):
    user = frappe.get_doc("User", user.name)
    return user.reset_password()


@frappe.whitelist(allow_guest=True)
def forgot_password(email):
    if not frappe.db.exists("User", email):
        return {'status': 'error', 'message': ('User with this email does not exist')}

    user = frappe.get_doc("User", email)
    reset_password_link = generate_reset_password_link(user)

    send_reset_password_email(user, reset_password_link)

    return {'status': 'success', 'message': ('Password reset link has been sent to your email')}


def generate_reset_password_link(user):
    reset_key = get_password_reset_key(user)
    return reset_key

def send_reset_password_email(user, reset_password_link):
    subject = ("Password Reset Request for GeoHosting")
    message = f"""
        <div style="font-family: Roboto; color: #333;">
            <h1>Password Reset Request</h1>
            <p>Hello {user.first_name},</p>
            <p>We received a request to reset your password for your GeoHosting account.</p>
            <p>Click on the link below to reset your password:</p>
            <a href="{reset_password_link}" 
            style="display: inline-block; padding: 10px 20px; 
            background-color: #F4B340; color: #fff; 
            text-decoration: none; border-radius: 5px;">Reset Password</a>
            <p>You can also copy-paste the following link in your browser:</p>
            <p><a href="{reset_password_link}">{reset_password_link}</a></p>
            <div style="margin-top: 30px; font-size: 0.8em; color: #666;">
                <p>Kartoza (Pty) Ltd.</p>
                <p>Company no: 2014/109067/07</p>
                <p>VAT Number: 4450266806</p>
                <p>Executive Directors: Tim Sutton MA; 
                Gavin Fleming MSc PrGISc [PGP1234] Non-Executive 
                Directors: Lawrence Hyslop M.Sc, MBA, PR Eng; Jenny Sutton MBA, LLM. Registered 
                Office: 28 Olienhout Street, Vermont, 7201, South Africa.</p>
                <p>Staff in South Africa (Gauteng, Western Cape, kwaZulu-Natal), Portugal, Indonesia and Tanzania</p>
                <p>Tel: +27 (0)73 768 8108 / +27 (0)87 809 2702</p>
                <p>Web: <a href="https://kartoza.com">https://kartoza.com</a> 
                Email: <a href="mailto:info@kartoza.com">info@kartoza.com</a></p>
                <p>Sent via ERPNext</p>
            </div>
        </div>
    """

    frappe.sendmail(recipients=user.email, subject=subject, message=message)
