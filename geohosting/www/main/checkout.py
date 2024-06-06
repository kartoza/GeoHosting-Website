import frappe, requests, json
from frappe_paystack.utils import (
    compute_received_hash, getip, is_paystack_ip,
    generate_digest,
)


@frappe.whitelist(allow_guest=True)
def get_payment_request(**kwargs):
    # Custom implementation
    try:
        data = frappe.form_dict
        
        if not frappe.db.exists(data.reference_doctype, data.reference_docname):
            # Create a new Payment Request document with the specified details
            payment_request = frappe.get_doc({
                "doctype": "Payment Request",
                "payment_request_type": "Inward",
                "mode_of_payment": "Credit Card",
                "party_type": "Customer",
                "party": data.customer,
                "reference_doctype": "Sales Order",
                "reference_name": data.sales_order,
                "grand_total": float(data.amount),
                "currency": data.currency,
                "is_subscription": 0, # TODO set to 1 once we set recurring payments
                "email_to": data.email,
                "subject": "Payment Request for " + data.sales_order,
                "message": "Please click on the link below to make your payment",
                # "payment_gateway_account": "Paystack ZAR",
                "payment_gateway": data.gateway,
                "payment_channel": "Email"
            })
            payment_request.insert(ignore_permissions=True)
            payment_request.save()
            frappe.db.commit()
        else:
            payment_request = frappe.get_doc(data.reference_doctype, data.reference_docname)

        paystack_gateway = frappe.get_doc("Payment Gateway", payment_request.payment_gateway)
        paystack = frappe.get_doc("Paystack Settings", paystack_gateway.gateway_controller)
        
        if payment_request.payment_request_type == 'Inward':
            ecommerce = frappe.get_single("E Commerce Settings")
            return dict(
                payment_request=payment_request,
                name=payment_request.name,
                email=data.email,
                currency=payment_request.currency,
                status=payment_request.status,
                public_key=paystack.get_public_key(),
                metadata={
                    'doctype': payment_request.doctype,
                    'docname': payment_request.name,
                    'reference_doctype': payment_request.reference_doctype,
                    'reference_name': payment_request.reference_name,
                    'gateway': payment_request.payment_gateway,
                }
            )
        else:
            frappe.throw(_('Only Inward payment allowed.'))
    except Exception as e:
        frappe.log_error(str(e), 'Custom Paystack')
        frappe.throw(_('Invalid Payment'))


@frappe.whitelist(allow_guest=True)
def verify_transaction(transaction):
    frappe.enqueue(queue_verify_transaction, transaction=transaction)

def queue_verify_transaction(transaction):
    # Custom implementation
    try:
        transaction = frappe._dict(json.loads(transaction))
        gateway = frappe.get_doc("Paystack Settings", transaction.gateway)
        secret_key = gateway.get_secret_key()
        headers = {"Authorization": f"Bearer {secret_key}"}
        req = requests.get(
            f"https://api.paystack.co/transaction/verify/{transaction.reference}",
            headers=headers, timeout=10
        )
        if req.status_code in [200, 201]:
            response = frappe._dict(req.json())
            data = frappe._dict(response.data)
            metadata = frappe._dict(data.metadata)
            if not frappe.db.exists("Paystack Log", {'name': data.reference}):
                frappe.get_doc({
                    'doctype': "Paystack Log",
                    'amount': data.amount / 100,
                    'currency': data.currency,
                    'message': response.message,
                    'status': data.status,
                    'reference': data.reference,
                    'payment_request': metadata.docname,
                    'reference_doctype': metadata.reference_doctype,
                    'reference_name': metadata.reference_name,
                    'transaction_id': data.id,
                    'data': response
                }).insert(ignore_permissions=True)
                frappe.db.commit()
                # Clear payment
                payment_request = frappe.get_doc('Payment Request', metadata.docname)
                integration_request = frappe.get_doc("Integration Request", {
                    'reference_doctype': metadata.doctype,
                    'reference_docname': metadata.docname})
                payment_request.run_method("on_payment_authorized", 'Completed')
                integration_request.db_set('status', 'Completed')
                frappe.db.commit()
        else:
            # Log error
            frappe.log_error(str(req.reason), 'Verify Transaction')
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + str(frappe.form_dict), 'Verify Transaction')


@frappe.whitelist(allow_guest=True)
def webhook(**kwargs):
    # Custom implementation
    try:
        transaction = frappe.form_dict
        data = frappe._dict(json.loads(transaction.data))
        metadata = frappe._dict(data.metadata)
        gateway = frappe.get_doc("Paystack Settings", metadata.gateway)
        secret_key = gateway.get_secret_key()
        headers = {"Authorization": f"Bearer {secret_key}"}
        req = requests.get(
            f"https://api.paystack.co/transaction/verify/{data.reference}",
            headers=headers, timeout=10
        )
        if req.status_code in [200, 201]:
            response = frappe._dict(req.json())
            data = frappe._dict(response.data)
            metadata = frappe._dict(data.metadata)
            frappe.get_doc({
                'doctype': "Paystack Log",
                'amount': data.amount / 100,
                'currency': data.currency,
                'message': response.message,
                'status': data.status,
                'reference': data.reference,
                'payment_request': metadata.docname,
                'reference_doctype': metadata.reference_doctype,
                'reference_name': metadata.reference_name,
                'transaction_id': data.id,
                'data': response
            }).insert(ignore_permissions=True)
            # Clear payment
            frappe.db.commit()
            payment_request = frappe.get_doc('Payment Request', metadata.docname)
            integration_request = frappe.get_doc("Integration Request", {
                'reference_doctype': metadata.doctype,
                'reference_docname': metadata.docname})
            payment_request.run_method("on_payment_authorized", 'Completed')
            integration_request.db_set('status', 'Completed')
            frappe.db.commit()
            # from here trigger adding product to user and spinning up geonode or whatever product purchased via api call to jenkins
            create_user_product(metadata.docname)
            # if this entry point is successful might need to update payment request , sales order and create sales invoice
        else:
            # Log error
            frappe.log_error(str(req.reason), 'Verify Transaction')
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + str(frappe.form_dict), 'Verify Transaction')



def create_user_product(payment_request_name):
    try:
        payment_request = frappe.get_doc('Payment Request', payment_request_name)
    except frappe.DoesNotExistError:
        frappe.log_error(f'Payment Request {payment_request_name} does not exist.')
        return

    # Define specifications based on item code prefix
    specifications_map = {
        "geonode": {
            "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "Specify medium specifications here",
            "LARGE": "Specify large specifications here"
        },
        "geosight": {
            # Specifications for geosight prefixes
        },
        "bims": {
            # Specifications for bims prefixes
        },
        "g3w": {
            # Specifications for g3w prefixes
        },
        "geoserver": {
            # Specifications for geoserver prefixes
        }
    }

    # Extract the purchased item details
    purchased_items = payment_request.items
    for item in purchased_items:
        try:
            # Split item code to extract prefix and size
            prefix, size, _ = item.item_code.split('-')

            # Get specifications based on prefix and size
            specifications = specifications_map.get(prefix.lower(), {}).get(size.upper(), "")

            # Attempt to create a User Products record
            user_product = frappe.get_doc({
                'doctype': 'User Products',
                'user': payment_request.email_to,
                'product': item.item_code,
                'specifications': specifications,
                'status': "Active",
                'product_meta': {
                    'url_path': f"https://kartoza-staging-v14.frappe.cloud/app/main/products",
                    'username': "Admin",
                    'password': "test"
                }
            })
            user_product.insert(ignore_permissions=True)
            frappe.db.commit()
        except frappe.DoesNotExistError:
            frappe.log_error('The doctype User Products does not exist.')
            return
        except Exception as e:
            frappe.log_error(f'Failed to create User Products for {payment_request.email_to}: {str(e)}')

