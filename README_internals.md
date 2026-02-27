# README_internals.md 

### C1
## 1. Auto-set Columns When Appending Child Row

When a row is appended to `Job Card.parts_used` and the document is saved, Frappe automatically sets these **4 columns** on the child table row:

* **parent** → Name of the parent document (Job Card ID)
* **parenttype** → Parent DocType (`Job Card`)
* **parentfield** → Field name holding the child table (`parts_used`)
* **idx** → Row order number inside the child table

---

## 2. Database Table Name

For a child DocType **Part Usage Entry**, the database table name is:

```
tabPart Usage Entry
```

Frappe automatically prefixes tables with **`tab`**.

---

## 3. Deleting Row at `idx = 2`

If the row with `idx = 2` is deleted and the document is saved:

* Frappe **reindexes** remaining rows automatically.
* `idx` values are reassigned sequentially starting from **1**.

Example:

Before delete:

```
idx: 1, 2, 3, 4
```

After deleting row 2:

```
idx: 1, 2, 3
```

### C3 
## Renaming Technician

After renaming a **Technician** using *Rename Document*, the
`assigned_technician` field in linked **Job Cards** updated automatically.

**Reason:**
`assigned_technician` is a **Link field**. Frappe maintains referential integrity and automatically updates all linked records when a document name changes.

---

## Track Changes

**Track Changes** records document modifications.
When enabled, Frappe creates a **Version** log storing:

* Old value
* New value
* User
* Timestamp

Used for auditing and history tracking.

---

## Unique Constraints

**DocType Unique Field**

* Database-level constraint
* Prevents duplicates permanently
* Safe against concurrent inserts

**`frappe.db.exists()` in validate()**

* Application-level check
* Custom validation logic
* Can fail in race conditions

**Difference:**
Unique field = database enforced uniqueness
`db.exists()` = manual validation check



### D2 - Permission Query & has_permissioncd a
Using frappe.get_all() in an whitelist method wont check the frappe's permission system, including permission_query_conditions. This means low-privilege users or guests can access records they are not supposed to see. It can cause serious data leakage.


### E1 on_update() - demonstrate the recursion pitfall:

`on_update()` runs after every save. Calling `save()` again triggers `on_update() `repeatedly:

save → on_update → save → on_update → ...

This leads to server freeze or RecursionError.

### E3 Why doc_events Is Safer Than override_doctype_class

`doc_events` is safer for most use cases because it extends behavior
instead of replacing it, preserving compatibility with future Frappe
updates. `override_doctype_class` should be reserved only for deep
customization where hooks are insufficient.
