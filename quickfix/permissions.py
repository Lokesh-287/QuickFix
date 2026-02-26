import frappe

def job_card_query(user):
    roles=frappe.get_roles(user)
    if (
        "Administrator" in roles
        or "System Manager" in roles
        or "QF Manager" in roles
        ):
        return "" 
    
    if "QF Technician"  in roles:
        f"""
    `tabJob Card`.assigned_technician  = '{user}'
"""

    return "1=0"
def service_invoice_has_permission(doc,user):
    roles=frappe.get_roles(user)
    
    if (
        "Administrator" in roles
        or "System Manager" in roles
        or "QF Manager" in roles
    ):
        return True
    
    isPaid=frappe.db.exists("Job Card",{
        "name":doc.job_card,
        "payment_status":"Paid"
    })
    if not isPaid:
        return False
    return True
    