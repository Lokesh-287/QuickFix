import frappe

def after_install():
    create_default_device_types()
    create_quickfix_settings()
    frappe.msgprint("QuickFix installed successfully By Lokiiiiiiiiiiiiiiiii")


def create_default_device_types():
    default_devices=[
        {
            "name": "Airpods",
            "description": "Used for music and calls",
            "average_repair_hours": 1,
        },{
             "name": "Laptop",
            "description": "Portable personal computer",
            "average_repair_hours": 4,
        },{
            "name": "Smartphone",
            "description": "Handheld communication device",
            "average_repair_hours": 2,
        }
    ]
    for device in default_devices:
        if not frappe.db.exists("Device Type",device["name"]):
            frappe.get_doc({
                "doctype":"Device Type",
                "device_type":device["name"],
                "description":device["description"],
                "average_repair_hours":device["average_repair_hours"]
            }).insert(ignore_permissions=True)
def create_quickfix_settings():
    settings=frappe.get_single("QuickFix Settings")
    settings.shop_name="QuickFix"
    settings.manager_email="lokeshkrishna383@gmail.com"
    settings.default_labour_charge=500
    settings.low_stock_alert_enabled=1
    settings.low_stock_threshold=5
    settings.save(ignore_permissions=True)