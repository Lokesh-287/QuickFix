import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please login to view your jobs")

    context.jobs = frappe.get_all(
        "Job Card",
        filters={"owner": frappe.session.user},
        fields=["name", "status", "creation"],
        order_by="creation desc"
    )