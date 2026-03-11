import frappe

def clear_status_chart_cache(doc, method):
    frappe.cache().delete_value("quickfix:status_chart_data")