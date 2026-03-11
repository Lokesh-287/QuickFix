import frappe
import json

@frappe.whitelist()
def get(chart_name=None, chart=None, no_cache=None, filters=None,
        from_date=None, to_date=None, timespan=None,
        time_interval=None, heatmap_year=None):
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    cache_key = "quickfix:status_chart_data"

    cached_data = frappe.cache().get_value(cache_key)
    if cached_data:
        return json.loads(cached_data)

    statuses = [
        "Draft",
        "Pending Diagnosis",
        "Awaiting Customer Approval",
        "In Repair",
        "Ready for Delivery",
        "Delivered",
        "Cancelled"
    ]

    labels = []
    values = []

    for status in statuses:
        count = frappe.db.count("Job Card", filters={"status": status})
        labels.append(status)
        values.append(count)

    result = {
        "labels": labels,
        "datasets": [{"name": "Job Cards", "values": values}],
        "type": "bar"
    }

    frappe.cache().set_value(
        cache_key,
        json.dumps(result),
        expires_in_sec=300
    )

    return result