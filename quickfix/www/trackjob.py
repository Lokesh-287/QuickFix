import frappe

def get_context(context):

    context.title = "Track Job Status"
    context.description = "Track repair job status using phone number"
    context.og_title = "QuickFix Job Tracking"

    phone = frappe.form_dict.get("phone")
    context.jobs = []

    frappe.logger().info(f"PHONE INPUT: {phone}")

    if phone:
        phone = "".join(filter(str.isdigit, phone))[:10]

        jobs = frappe.db.get_all(
            "Job Card",
            filters={"customer_phone": phone},
            fields=["name", "status"]
        )

        frappe.logger().info(f"JOBS FOUND: {jobs}")

        context.jobs = jobs