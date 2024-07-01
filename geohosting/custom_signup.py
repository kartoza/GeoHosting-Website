import frappe
from frappe.auth import Signup


class CustomSignup(Signup):
    def send_welcome_email(self):
        """Send a customised email welcome to new users from geoHosting."""

        subject = "Welcome to GeoHosting"
        message = f"""
        <div style="font-family: Roboto; color: #333;">
            <h1>Welcome to GeoHosting</h1>
            <p>Hello {self.user.first_name},</p>
            <p>A new account has been created for you at <a href="{frappe.utils.get_url()}">
            {frappe.utils.get_url()}</a>.</p>
            <p>Your login id is: {self.user.email}</p>
            <p>Click on the link below to complete your registration and set a new password.</p>
            <a href="{frappe.utils.get_url()}/update-password?key={self.get_password_reset_key()}" 
            style="display: inline-block; padding: 10px 20px; 
            background-color: #F4B340; color: #fff; 
            text-decoration: none; border-radius: 5px;">Complete Registration</a>
            <p>You can also copy-paste the following link in your browser:</p>
            <p><a href="{frappe.utils.get_url()}/update-password?key={self.get_password_reset_key()}">
            {frappe.utils.get_url()}/update-password?key={self.get_password_reset_key()}</a></p>
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

        frappe.sendmail(recipients=self.user.email, subject=subject, message=message)

    def signup(self):
        super().signup()
        self.send_welcome_email()
