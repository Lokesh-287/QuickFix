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

#This is unsafe so i commented this function :(
# @frappe.whitelist(allow_guest=True)
# def get_job_cards_unsafe():

#     # Ignores permissions
#     # Returns ALL fields
#     # Exposes sensitive data

#     return frappe.get_all(
#         "Job Card",
#         fields="*"
#     )

@frappe.whitelist()
def get_job_cards_safe():

    user = frappe.session.user
    roles = frappe.get_roles(user)

    job_cards = frappe.get_list(
        "Job Card",
        fields=[
            "name",
            "customer_name",
            "assigned_technician",
            "status",
            "payment_status"
        ]
    )

    # Remove sensitive data for non-managers
    if not {"Administrator", "System Manager", "QF Manager"} & set(roles):

        for jc in job_cards:
            jc.pop("customer_phone", None)
            jc.pop("customer_email", None)

    return job_cards

@frappe.whitelist()
def send_job_ready_email(job_name):
    job = frappe.get_doc("Job Card", job_name)
    frappe.sendmail(
        recipients=[job.owner],
        subject="Job Ready",
        message=f"Job {job.name} is completed."
    )


@frappe.whitelist()
def custom_get_count(doctype,filters=None,debug=False,cache=False):
    # print("!!!!!!!!!!!!!!!!!!!!!!!11")
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doctype,
        "action": "count_queried",
        "user": frappe.session.user
    }).insert(ignore_permissions=True)
    from frappe.client import get_count
    return get_count(doctype,filters,debug,cache)

@frappe.whitelist()
def mark_as_delivered(job_card):
    frappe.db.set_value("Job Card",job_card,"status","Delivered")
    