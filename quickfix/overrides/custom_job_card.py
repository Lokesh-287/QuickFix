from quickfix.service_center.doctype.job_card.job_card import JobCard
import frappe

class CustomJobCard(JobCard):

    def validate(self):
        super().validate() # ALWAYS call super first
        self._check_urgent_unassigned()

    def _check_urgent_unassigned(self):
        if self.priority == "Urgent" and not self.assigned_technician:
            settings = frappe.get_single("QuickFix Settings")
            frappe.enqueue("quickfix.utils.send_urgent_alert",
                            job_card=self.name, manager=settings.manager_email)


"""
----------------------------
Method Resolution Order (MRO)
-----------------------------

Method Resolution Order (MRO) defines the order in which Python searches
for a method when multiple classes are involved in inheritance. Python
checks the child class first and then continues searching parent classes
according to the MRO chain.

In Frappe, when we override a DocType using override_doctype_class,
our custom class inherits from the original core DocType class and
ultimately from frappe.model.document.Document.

--------------------------------------
Why calling super() is NON-NEGOTIABLE:
--------------------------------------

When we override lifecycle methods such as validate(), Python will execute
only the custom method unless super() is explicitly called.

Calling super().validate() continues execution to the parent class
implementation in the MRO chain so that Frappe’s core logic still runs.

This is important because:

- Frappe core validations, permissions, and workflow logic exist
  inside the parent validate() method.
- If super() is skipped, core framework behavior is bypassed.
- Future framework updates may introduce new validations in the
  core class, and those changes will NOT reflect in the custom class
  if super() is not used.

Therefore, super() ensures:
- framework stability
- forward compatibility with future updates
- preservation of core validation behavior

-----------------------------------------------------
When to Choose override_doctype_class over doc_events
-----------------------------------------------------

Frappe provides two customization approaches: doc_events and
override_doctype_class.

doc_events are used to ATTACH additional logic to document lifecycle
events without changing the original DocType class. They are ideal for
lightweight extensions such as notifications, logging, or small
validations.

override_doctype_class is chosen when deeper customization is required.
It replaces the original DocType Python class with a custom class that
inherits from the core implementation.

Choose override_doctype_class when:
- core business logic must be modified or controlled
- default lifecycle behavior needs to be changed
- existing methods like validate(), save(), or permissions must be
  overridden
- inheritance and Method Resolution Order (MRO) behavior must be managed
- customization cannot be achieved using simple event hooks

-----------------------------------------------------------------
## Why doc_events Is Safer Than override_doctype_class
-----------------------------------------------------------------


`doc_events` is safer for most use cases because it extends behavior
instead of replacing it, preserving compatibility with future Frappe
updates. `override_doctype_class` should be reserved only for deep
customization where hooks are insufficient.
    """