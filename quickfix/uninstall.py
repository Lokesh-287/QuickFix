import frappe

def before_uninstall():
    check_submitted_job_card()

def check_submitted_job_card():
    if frappe.db.exists("Job Card",{
        "docstatus":1
    }):
        frappe.throw("Cannot uninstall QuickFix App ,Submitted Job Cards exist in the system cancel or delete them before uninstalling")
