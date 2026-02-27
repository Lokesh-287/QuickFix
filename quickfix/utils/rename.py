import frappe

@frappe.whitelist()
def rename_technician(old_name, new_name):
    frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )

"""
merge=False prevents renaming when the target name already exists,
while merge=True merges both documents and updates all linked records,
which can be dangerous because the original document identity is lost.
"""