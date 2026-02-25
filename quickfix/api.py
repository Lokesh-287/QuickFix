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


@frappe.whitelist()
def share_job_card(job_card_name, user_email):

    frappe.share.add(
        "Job Card",
        job_card_name,
        user_email,
        read=1,
        write=0,
        share=0
    )

    return "Job Card shared successfully"

@frappe.whitelist()
def manager_only_action():

    frappe.only_for("QF Manager")

    return {
        "value":"Manager operation executed"
    }

