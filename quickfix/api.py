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
    if not job.customer_email:
        return
    frappe.sendmail(
        recipients=[job.customer_email],
        subject="Job Ready",
        message=f"Job {job.name} is completed."
    )


@frappe.whitelist()
def custom_get_count(doctype,filters=None,debug=False,cache=False):
    print("!!!!!!!!!!!!!!!!!!!!!!!11")
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
    
@frappe.whitelist()
def mark_ready(job_card):
    frappe.db.set_value("Job Card",job_card,"status","Ready for Delivery")


@frappe.whitelist()
def enqueue_technician_performance_report(filters=None):
    """
    Trigger a background generation of the Technician Performance Report.

    We do NOT call frappe.enqueue() directly here.
    Instead, we insert a Prepared Report document.
    Frappe's own after_insert hook on the Prepared Report DocType
    automatically enqueues the background job to run execute()
    and store the result.
    """
    doc = frappe.get_doc({
        "doctype": "Prepared Report",
        "report_name": "Technician Performance Report",
        "filters": frappe.as_json(filters or {}),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.msgprint(
        f"Report queued successfully. Prepared Report: {doc.name}"
    )
    return doc.name


# @frappe.whitelist()
# def get_status_chart_data():

#     data = frappe.db.sql("""
#         SELECT status, COUNT(name) as count
#         FROM `tabJob Card`
#         GROUP BY status
#     """, as_dict=True)

#     labels = []
#     values = []

#     for d in data:
#         labels.append(d.status)
#         values.append(d.count)

#     # return {
#     #     "labels": labels,
#     #     "datasets": [
#     #         {
#     #             "name": "Job Count",
#     #             "values": values
#     #         }
#     #     ]
#     # }
#     result = {
#         "labels": labels,
#         "datasets": [
#             {
#                 "name": "Job Status",
#                 "values": values
#             }
#         ]
#     }

#     # cache for 300 seconds
#     frappe.cache().set_value(cache_key, result, expires_in_sec=300)

#     return result
from frappe.utils import today
@frappe.whitelist()
def check_low_stock():
    last_run=frappe.db.get_value(
        "Audit Log",{
            "action":"low_stock_check",
            "creation":[">=",today()]
        },"name"
    )
    if last_run:
        return # already Ran today ,skip
    
    settings=frappe.get_single("QuickFix Settings")
    low_stock_parts=frappe.get_list(
        "Spare Part",
        filters=[
        ["stock_qty","<=",settings.low_stock_threshold or 5],
        ["is_active","=",1]
        ],
        fields=["name","part_name","stock_qty","reorder_level"] 
                    )
    if low_stock_parts and settings.low_stock_alert_enabled and settings.manager_email:
        part_list = "".join(
            f"<li>{p.part_name} — Stock: {p.stock_qty}, Reorder at: {p.reorder_level}</li>"
            for p in low_stock_parts
        )
        frappe.sendmail(
            recipients=[settings.manager_email],
            subject="QuickFix Low Stock Alert",
            message=f"<p>Parts below reorder level:</p><ul>{part_list}</ul>"
        )

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Spare Part",
        "document_name": "low_stock_check",
        "action": "low_stock_check",
        "user": frappe.session.user,
    }).insert(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def deliberate_failing_job():
    """
    Deliberately fails to demonstrate:
    - Error Log creation
    - RQ Failed Jobs
    - Retry behavior
    """
    frappe.logger("quickfix").info("Deliberate failing job started")
    raise Exception("This is a deliberate failure for Task D demonstration")

###      K3 - Performance Engineering
## Task B - Bulk operations:
## 1. Cancel 1000 Draft Job Cards — single SQL UPDATE

# def cancel_old_draft_job_cards():
#     frappe.db.sql("""
#         UPDATE `tabJob Card`
#         SET
#             status = 'Cancelled',
#             modified = NOW(),
#             modified_by = 'Administrator'
#         WHERE
#             status = 'Draft'
#             AND creation < DATE_SUB(NOW(), INTERVAL 30 DAY)
#         LIMIT 1000
#     """)
#     frappe.db.commit()

## 2. Insert 500 Audit Logs — bulk_insert

# def insert_audit_logs_bulk():

    # logs = []

    # for i in range(500):
    #     logs.append((
    #         str(uuid.uuid4()),  # name
    #         "Cancel Job Card",  # action
    #         frappe.session.user # user
    #     ))

    # frappe.db.bulk_insert(
    #     "Audit Log",
    #     ["name", "action", "user"],
    #     logs
    # )

    # # frappe.db.commit()

    # print("500 Audit Logs inserted using bulk_insert")

## 3. Benchmark — run in bench console

## import time
# import frappe

# start = time.time()

# for i in range(500):
#     log = frappe.get_doc({
#         "doctype": "Audit Log",
#         "action": "Test Insert",
#         "user": frappe.session.user
#     })
#     log.insert()

# frappe.db.commit()

# end = time.time()

# print("Time using insert():", end - start)
# ------------------------------
# import time
# import uuid

# start = time.time()

# logs = []

# for i in range(500):
#     logs.append((
#         str(uuid.uuid4()),
#         "Test Bulk Insert",
#         frappe.session.user
#     ))

# frappe.db.bulk_insert(
#     "Audit Log",
#     ["name", "action", "user"],
#     logs
# )

# frappe.db.commit()

# end = time.time()

# print("Time using bulk_insert():", end - start)

from frappe.utils import getdate

@frappe.whitelist(allow_guest=True)
def get_job_summary():
    
    # Read parameter from request
    job_card_name = frappe.form_dict.get("job_card_name")

    if not job_card_name:
        frappe.local.response["http_status_code"] = 400
        return {"error": "job_card_name parameter required"}

    # Check if job exists
    if not frappe.db.exists("Job Card", job_card_name):
        frappe.local.response["http_status_code"] = 404
        return {"error": "Not found"}

    # Fetch only required fields (avoid sensitive fields)
    job = frappe.db.get_value(
        "Job Card",
        job_card_name,
        ["name", "status", "assigned_technician", "creation", "modified"],
        as_dict=True
    )

    # Convert creation to Python date object
    created_date = getdate(job.creation)

    # Return summary dict
    return {
        "job_card": job.name,
        "status": job.status,
        "technician": job.assigned_technician,
        "created_date": created_date
    }

import time

@frappe.whitelist(allow_guest=True)
def get_job_by_phone():

    phone = frappe.form_dict.get("phone")

    # get client IP
    ip = frappe.local.request_ip

    cache = frappe.cache()

    # key per IP per minute
    minute = int(time.time() / 60)
    key = f"rate_limit:{ip}:{minute}"

    count = cache.get_value(key) or 0

    # limit: 10 requests per minute
    if int(count) >= 10:
        frappe.local.response["http_status_code"] = 429
        return {"error": "Too many requests"}

    cache.set_value(key, int(count) + 1, expires_in_sec=60)

    jobs = frappe.get_all(
        "Job Card",
        filters={"customer_phone": phone},
        fields=["name", "status", "assigned_technician"]
    )

    return {"jobs": jobs}


import hmac
import hashlib
import json

# @frappe.whitelist(allow_guest=True)
# def payment_webhook():

#     # 1. Read raw request body
#     payload = frappe.request.data

#     # 2. Validate HMAC signature
#     secret = frappe.conf.get("payment_webhook_secret", "")
#     signature = frappe.get_request_header("X-Signature")

#     expected = hmac.new(
#         secret.encode(),
#         payload,
#         hashlib.sha256
#     ).hexdigest()

#     if not hmac.compare_digest(expected, signature or ""):
#         frappe.throw("Invalid signature", frappe.AuthenticationError)

#     # 3. Parse payload
#     data = json.loads(payload)

#     reference = data.get("ref")

#     # 4. Deduplication check
#     if frappe.db.exists(
#         "Audit Log",
#         {
#             "action": "payment_received",
#             "document_name": reference
#         }
#     ):
#         return {
#             "status": "duplicate",
#             "message": "Already processed"
#         }

#     # 5. Update Job Card or Service Invoice
#     if frappe.db.exists("Job Card", reference):

#         job = frappe.get_doc("Job Card", reference)
#         job.payment_status = "Paid"
#         job.save(ignore_permissions=True)

#     # 6. Log event to Audit Log
#     audit = frappe.get_doc({
#         "doctype": "Audit Log",
#         "action": "payment_received",
#         "document_name": reference,
#         "status": "Success"
#     })

#     audit.insert(ignore_permissions=True)

#     frappe.db.commit()

#     return {
#         "status": "ok",
#         "message": "Payment processed"
#     }

@frappe.whitelist(allow_guest=True)
def payment_webhook():

    logger = frappe.logger("quickfix")

    try:
        logger.info("Payment webhook triggered")

        payload = frappe.request.data
        logger.info(f"Received payload: {payload}")

        signature = frappe.get_request_header("X-Signature")

        if not signature:
            logger.warning("Missing X-Signature header")
            frappe.throw("Invalid request")

        # Example processing
        logger.info("Processing payment confirmation")

        return {"status": "success"}

    except Exception:
        logger.error("Error occurred in payment webhook")

        frappe.log_error(
            title="Payment Webhook Failure",
            message=frappe.get_traceback()
        )

        return {"status": "error"}