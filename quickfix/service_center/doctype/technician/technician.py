# Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class Technician(WebsiteGenerator):
	def after_insert(self):
		self.create_user()
	
	def create_user(self):

		if frappe.db.exists("User",self.email) :
			return
		
		user = frappe.get_doc({
      "doctype": "User",
      "email": self.email,
      "first_name": self.technician_name,
      "enabled": 1,

      "send_welcome_email": 1,

      "roles": [
        {"role": "QF Technician"}
      ]
    })
		user.insert()
		self.user = user.email

