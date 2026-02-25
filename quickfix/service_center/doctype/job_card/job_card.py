# Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		if not self.labour_charge:
			self.labour_charge=frappe.db.get_single_value("QuickFix Settings","default_labour_charge")