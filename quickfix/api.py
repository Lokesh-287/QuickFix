import frappe

@frappe.whitelist()
def get_job_summary():
    return {
        "message": "API method working",
        "user": frappe.session.user
    }


@frappe.whitelist()
def test_exception():
    raise Exception("Manual Exception Raised")