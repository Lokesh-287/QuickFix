import frappe
import requests
import hashlib


def send_webhook(job_card_name, retry_count=0):

    settings = frappe.get_single("QuickFix Settings")

    if not settings.webhook_url:
        return

    doc = frappe.get_doc("Job Card", job_card_name)

    payload = {
        "event": "job_submitted",
        "job_card": doc.name,
        "customer_name": doc.customer_name,
        "customer_phone": doc.customer_phone,
        "device_type": doc.device_type,
        "device_brand": doc.device_brand,
        "device_model": doc.device_model,
        "amount": doc.final_amount,
        "status": doc.status
    }

    webhook_id = hashlib.sha256(
        f"{doc.name}-job_submitted".encode()
    ).hexdigest()

    # Deduplication check
    if frappe.db.exists("Audit Log", {"webhook_id": webhook_id}):
        return

    try:

        response = requests.post(
            settings.webhook_url,
            json=payload,
            timeout=5
        )

        response.raise_for_status()

        frappe.get_doc({
            "doctype": "Audit Log",
            "action": "webhook_sent",
            "document_name": doc.name,
            "webhook_id": webhook_id
        }).insert(ignore_permissions=True)

    except Exception as e:

        frappe.log_error(str(e), "Webhook Error")

        if retry_count < 3:
            frappe.enqueue(
                "quickfix.webhooks.send_webhook",
                job_card_name=job_card_name,
                retry_count=retry_count + 1,
                delay=60
            )