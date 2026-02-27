# Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SparePart(Document):
	def autoname(self):
		self.name=self.part_code.upper()+"-"+self.make_autoname("PART-.YYYY.-.####")

	def validate(self):
		# checking selling price > unit cost
		
		if not (self.selling_price>self.unit_cost):
			frappe.throw("Selling Price must be greater than Unit Cost")
			
	def on_update(self):
		threshold = frappe.db.get_value(
            "QuickFix Settings",
            None,
            "low_stock_threshold"
        )
		if self.stock_qty <= threshold:
			frappe.msgprint("Stock below threshold")

		"""
I use frappe.db.get_value instead of frappe.get_doc because only a
single field (low_stock_threshold) is required.

frappe.get_doc loads the entire document object including metadata,
permissions, and child tables, which is unnecessary and slower for
simple read operations.

frappe.db.get_value performs a direct database query and fetches only
the required field, making it more efficient and better suited for
controller methods like on_update that run frequently.
"""