# Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		if not self.labour_charge:
			self.labour_charge=frappe.db.get_single_value("QuickFix Settings","default_labour_charge")


	def validate(self):
		self.check_customer_phone()
		self.check_status()
		self.set_values()

	def before_submit(self):
		self.validate_ready_for_delivery()
		self.check_stock()
	
	def on_submit(self):
		from quickfix.api import send_job_ready_email
		self.update_stock()
		self.create_invoice()
		self.send_socket_notification()
		self.enqueue_webhooks()
		
		frappe.enqueue(send_job_ready_email(self.name), queue="short")

	def on_cancel(self):
		self.status="Cancelled"
		self.restore_stock_qty()
		self.cancel_service_invoice()

	def enqueue_webhooks(self):
		frappe.enqueue(
			"quickfix.webhooks.send_webhook",
			job_card_name=self.name,
			retry_count=0
    	)

	def cancel_service_invoice(self):
		service_invoice=frappe.db.get_value("Service Invoice",{
			"job_card":self.name
		},"name")
		if service_invoice:
			service_invoice_doc=frappe.get_doc("Service Invoice",service_invoice)
			service_invoice_doc.cancel()
	
	def on_trash(self):
		if self.status != "Cancelled" and self.status != "Draft":
			frappe.throw(f"Cannot delete Job Card when status is {self.status}")
	
	def restore_stock_qty(self):
		parts={}
		for row in self.parts_used:
			parts[row.part]=parts.get(row.part,0)+(row.quantity or 0)
		for part,quantity in parts.items():
			doc = frappe.get_doc("Spare Part", part)
			current_qty= doc.stock_qty or 0
			new_qty=current_qty+quantity
			#ignore_permissions=True use pannalam because stock deduction system automatic ha nadakkuthu, user manual ha stock edit panala.
			doc.stock_qty = new_qty
			doc.save(ignore_permissions=True)
			# frappe.db.set_value("Spare Part",part,"stock_qty",new_qty,ignore_permissions=True)
	
#socket is nothing but sending some message that target user will recive a real time message without refersh like whatsapp
	def send_socket_notification(self):
		frappe.publish_realtime("job_ready",{
			"job_card":self.name,
			"message":"Job Completed"
		},user=self.owner)


	def create_invoice(self):
		frappe.get_doc({
			"doctype":"Service Invoice",
			"job_card":self.name,
			"customer_name":self.customer_name,
			"labour_charge":self.labour_charge,
			"parts_total":self.parts_total,
			"total_amount":self.final_amount,
			"payment_status":self.payment_status
		}).insert(ignore_permissions=True)


	def update_stock(self):
		parts={}
		for row in self.parts_used:
			parts[row.part]=parts.get(row.part,0)+(row.quantity or 0)
		for part,quantity in parts.items():
			doc = frappe.get_doc("Spare Part", part)

			current_qty=doc.stock_qty or 0
			new_qty=current_qty-quantity
			if new_qty < 0:
				frappe.throw(f"Stock cannot go negative for {part}")
			doc.stock_qty = new_qty
			doc.save(ignore_permissions=True)
			#ignore_permissions=True use pannalam because stock deduction system automatic ha nadakkuthu, user manual ha stock edit panala.
			# frappe.db.set_value("Spare Part",part,"stock_qty",new_qty,ignore_permissions=True)



	def validate_ready_for_delivery(self):
		if self.status!="Ready for Delivery":
			frappe.throw("Job Card must be 'Ready for Delivery' before submission")
	
	def check_stock(self):
		parts={}
		for row in self.parts_used:
			parts[row.part]=parts.get(row.part,0)+(row.quantity or 0)
		for part,quantity in parts.items():
			qty=frappe.db.get_value("Spare Part",part,"stock_qty") or 0 
			if(qty<quantity):
				frappe.throw(f"{part} qty is Insufficient")

	def check_customer_phone(self):
		if not self.customer_phone or not self.customer_phone.isdigit() or  len(self.customer_phone) != 10:
			frappe.throw("Invalid Phone number")

	def check_status(self):
		repair_stages = [ "In Repair", "Ready for Delivery", "Delivered" ]
		if self.status  in repair_stages and not self.assigned_technician :
			frappe.throw(f"Technician Must Exist if status in {self.status}")
	
	def set_values(self):
		total=0
		for row in self.parts_used:
			row.total_price=(row.quantity or 0 )* (row.unit_price or 0)
			total+=row.total_price
		self.parts_total=total
		if not self.labour_charge:
			self.labour_charge=frappe.db.get_single_value("QuickFix Settings","default_labour_charge")
		self.final_amount=self.parts_total+self.labour_charge
		self.dummy=self.final_amount
	
	def before_print(self, settings=None):
		"""
		Pre-compute data here and attach to self.
		Never put heavy logic inside the Jinja template directly.
		"""
		# Required by task
		self.print_summary = f"{self.customer_name} - {self.device_brand} {self.device_model}"
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		# Pre-compute QR code as base64 here, not in template
		

@frappe.whitelist()
def send_job_ready_email(job_name):
    job = frappe.get_doc("Job Card", job_name)
    if not job.customer_email:
        print("\n\n\nxuroer \\n\n\n\n")
        return
    frappe.sendmail(
        recipients=[job.customer_email],
        subject="Job Ready",
        message=f"Job {job.name} is completed."
    )