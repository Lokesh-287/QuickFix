import frappe

def job_card_query(user):
    roles=frappe.get_roles(user)
    if "Administrator" in roles:
        return
    if "QF Technician" not in roles:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return""

    return f"""
    `tabJob Card`.assigned_technician  = '{user}'
"""