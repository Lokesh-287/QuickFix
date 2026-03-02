
import frappe

from frappe.utils import now

def on_session_creation(login_manager):# here it automatically recives login manager but we dont need this because it already contains logged-in user

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "User",
        "document_name": frappe.session.user,
        "action": "Login",
        "user": frappe.session.user,
        "timestamp": now()
    }).insert(ignore_permissions=True)

def on_logout(login_manager):

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "User",
        "document_name": frappe.session.user,
        "action": "Logout",
        "user": frappe.session.user,
        "timestamp": now()
    }).insert(ignore_permissions=True)