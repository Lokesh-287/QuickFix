import frappe

def get_shop_name():
    return frappe.db.get_single_value("QuickFix Settings", "shop_name")

# def get_qr_code(self):
# 	"""Generate QR code for the Job Card URL as base64 string."""
# 	import qrcode
# 	import base64
# 	from io import BytesIO
# 	site_url = frappe.utils.get_url()
# 	job_url = f"{site_url}/job-card/{self.name}"
# 	qr = qrcode.make(job_url)
# 	buffer = BytesIO()
# 	qr.save(buffer, format="PNG")
# 	encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
# 	return encoded

def get_qr_code(job_card_name):
    import qrcode
    import base64
    from io import BytesIO

    site_url = frappe.utils.get_url()
    job_url = f"{site_url}/job-card/{job_card_name}"

    qr = qrcode.make(job_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def format_job_id(value):
    return "JOB#" + str(value)