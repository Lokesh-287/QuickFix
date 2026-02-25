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
			
		
   