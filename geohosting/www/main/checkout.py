import re
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
                "payment_gateway_account": "Paystack - ZAR",
                # "payment_gateway": data.gateway,
                # "payment_channel": "Email"
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
    try:
        # Synchronously verify the transaction and return the response to the frontend
        response = queue_verify_transaction(transaction)
        return response
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def queue_verify_transaction(transaction):
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

                payment_request = frappe.get_doc('Payment Request', metadata.docname)
                integration_request = frappe.db.exists({
                    'doctype': 'Integration Request',
                    'reference_doctype': metadata.doctype,
                    'reference_docname': metadata.docname
                })
                
                if not integration_request:
                    integration_request = frappe.get_doc({
                        'doctype': 'Integration Request',
                        'reference_doctype': metadata.doctype,
                        'reference_docname': metadata.docname
                    })
                    integration_request.insert(ignore_permissions=True)
                
                frappe.db.set_value("Integration Request", integration_request.name, 'status', 'Completed')
                payment_request.run_method("on_payment_authorized", 'Completed')
                frappe.db.commit()

            sales_order = frappe.get_doc('Sales Order', transaction.reference.split('=')[1])
            if sales_order:
                if sales_order.docstatus == 0:
                    sales_order.db_set('status', 'Completed')
                    sales_order.db_set('per_delivered', 100)
                    sales_order.db_set('per_billed', 100)
                    
                    # Save the document
                    # sales_order.save(ignore_permissions=True)
                    sales_order.submit()
                    frappe.db.commit()

                create_user_product(transaction.reference.split('=')[0], sales_order)
                
            return {'status': 'success', 'message': 'Transaction verified and processed successfully.'}
        else:
            frappe.log_error(str(req.reason), 'Verify Transaction')
            return {'status': 'error', 'message': str(req.reason)}
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + str(frappe.form_dict), 'Verify Transaction')
        return {'status': 'error', 'message': str(e)}


# @frappe.whitelist(allow_guest=True)
# def webhook(**kwargs):
#     # Custom implementation
#     try:
#         transaction = frappe.form_dict
#         data = frappe._dict(json.loads(transaction.data))
#         metadata = frappe._dict(data.metadata)

#         gateway = frappe.get_doc("Paystack Settings", metadata.gateway)
#         secret_key = gateway.get_secret_key()
#         headers = {"Authorization": f"Bearer {secret_key}"}
#         req = requests.get(
#             f"https://api.paystack.co/transaction/verify/{data.reference}",
#             headers=headers, timeout=10
#         )
#         if req.status_code in [200, 201]:
#             response = frappe._dict(req.json())
#             data = frappe._dict(response.data)
#             metadata = frappe._dict(data.metadata)
#             frappe.get_doc({
#                 'doctype': "Paystack Log",
#                 'amount': data.amount / 100,
#                 'currency': data.currency,
#                 'message': response.message,
#                 'status': data.status,
#                 'reference': data.reference,
#                 'payment_request': metadata.docname,
#                 'reference_doctype': metadata.reference_doctype,
#                 'reference_name': metadata.reference_name,
#                 'transaction_id': data.id,
#                 'data': response
#             }).insert(ignore_permissions=True)
#             frappe.db.commit()

#             payment_request = frappe.get_doc('Payment Request', metadata.docname)
#             integration_request = frappe.get_doc("Integration Request", {
#                         'reference_doctype': metadata.doctype,
#                         'reference_docname': metadata.docname
#             })

#             if not integration_request:
#                 integration_request = frappe.new_doc("Integration Request")
#                 integration_request.update({
#                             'reference_doctype': metadata.doctype,
#                             'reference_docname': metadata.docname
#                 })

#             payment_request.run_method("on_payment_authorized", 'Completed')
#             integration_request.db_set('status', 'Completed')
#             frappe.db.commit()

#             sales_order = frappe.get_doc('Sales Order', metadata.reference_name.split('=')[1])
#             if sales_order:
#                 if sales_order.docstatus == 0:
#                     sales_order.db_set('status', 'Completed')
#                     sales_order.db_set('per_delivered', 100)
#                     sales_order.db_set('per_billed', 100)
                    
#                     # Save the document
#                     sales_order.save(ignore_permissions=True)
#                     sales_order.submit()
#                     frappe.db.commit()
#                 create_user_product(metadata.reference_name.split('=')[1], sales_order)
#         else:
#             # Log error
#             frappe.log_error(str(req.reason), 'Verify Transaction')
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback() + str(frappe.form_dict), 'Verify Transaction')


def create_user_product(payment_request_name, sales_order=None):
    try:
        payment_request = frappe.get_doc('Payment Request', payment_request_name)
    except frappe.DoesNotExistError:
        frappe.log_error(f'Payment Request {payment_request_name} does not exist.')
        return

    if not sales_order:
        sales_order_name = payment_request.reference_name
        try:
            sales_order = frappe.get_doc('Sales Order', sales_order_name)
        except frappe.DoesNotExistError:
            frappe.log_error(f'Sales Order {sales_order_name} referenced in Payment Request {payment_request_name} does not exist.')
            return

    # Define specifications based on item code prefix and size example TODO extract specs from db
    specifications_map = {
        "geonode": {
            "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "4 CPUs, 8GB RAM, 80GB Storage",
            "LARGE": "8 CPUs, 16GB RAM, 120GB Storage"
        },
        "geosight": {
            "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "4 CPUs, 8GB RAM, 80GB Storage",
            "LARGE": "8 CPUs, 16GB RAM, 120GB Storage"
        },
        "bims": {
            "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "4 CPUs, 8GB RAM, 80GB Storage",
            "LARGE": "8 CPUs, 16GB RAM, 120GB Storage"
        },
        "g3w": {
           "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "Specify medium specifications here",
            "LARGE": "Specify large specifications here"
        },
        "geoserver": {
           "SMALL": "2 CPUs, 8GB RAM, 60GB Storage",
            "MEDIUM": "Specify medium specifications here",
            "LARGE": "Specify large specifications here"
        }
    }

    MAX_NAME_LENGTH = 140



    for item in sales_order.items:
        try:
            prefix, size, _ = item.item_code.split('-')

            specifications = specifications_map.get(prefix.lower(), {}).get(size.upper(), "")
            
            name = item.item_code[:MAX_NAME_LENGTH]

            logo = '/assets/geohosting/images/' + item.item_code.split('-')[0].upper() + '.svg'

            # Create User Products record TODO add dynamic data after jenkins creates product
            user_product = frappe.get_doc({
                'doctype': 'User Products',
                'name': name,
                'user': payment_request.email_to,
                'product': item.item_code,
                'specifications': {
                    "specifications": specifications
                },
                'status': "Active",
                'product_meta': {
                    'url_path': f"https://kartoza-staging-v14.frappe.cloud/app/main/products",
                    'username': "Admin",
                    'password': "test"
                },
                'logo': logo
            })
            user_product.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f'Failed to create User Products for {payment_request.email_to}: {str(e)}')
            continue

    frappe.db.commit()


def create_sales_invoice(sales_order):
    # TODO might not need to create one since this might be an automated transaction on subscriptions
    pass