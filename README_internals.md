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

save -> on_update -> save -> on_update → ...

This leads to server freeze or RecursionError.

### E3 Why doc_events Is Safer Than override_doctype_class

`doc_events` is safer for most use cases because it extends behavior
instead of replacing it, preserving compatibility with future Frappe
updates. `override_doctype_class` should be reserved only for deep
customization where hooks are insufficient.

### Multiple Validate Handlers Order

When both controller and doc_events handlers exist:

Execution order:

* Controller validate() method

* Specific DocType doc_events handler

* Wildcard "*" handler

If both handlers raise frappe.ValidationError, execution stops at the first
exception and remaining handlers do not execute.

### Wildcard + Specific DocType Conflict

If both "*" and a specific DocType handler are registered for the same event,
both handlers run.

Specific handler runs before wildcard handler.

#### F3 - Asset, Jinja & Website Hooks (5 pts)

### app_include_js vs web_include_js
## app_include_js

Loads JavaScript only inside the Desk (/app).

Used for internal logged-in users (Admin, Employee, Manager).

Affects forms, list views, reports, navbar, etc. inside Desk UI.

Not loaded on website or portal pages.

## When to use:

Customizing DocType behavior globally

Modifying Desk navbar/sidebar

Adding client scripts that should work across the Desk

## web_include_js

Loads JavaScript only on Website & Portal pages.

Used for public users or external logged-in users (Customer, Supplier).

Works on pages under /www or portal routes.

Not loaded inside Desk.

## When to use:

Custom website UI interactions

Portal page logic (e.g., customer dashboard)

Public page animations or validations

### doctype_js (Job Card)

doctype_js loads JavaScript only in the Form view of the Job Card DocType.
It is used to control client-side behavior such as field logic, validations, custom buttons, and event handling.
It affects only that specific DocType form inside Desk.

### doctype_list_js (Job Card)

doctype_list_js loads JavaScript only in the List view of the Job Card DocType.
It is used to customize how records appear and behave in the list page, such as indicators, filters, and list-level actions.

### doctype_tree_js

doctype_tree_js is used for DocTypes that represent hierarchical (parent-child) data.
It applies to DocTypes like Account, Item Group, Territory, or Department, where records are arranged in a tree structure.

Job Card is a transactional DocType without hierarchy, so tree view is not applicable.

### Build Cache-Busting

The command:

`bench build --app quickfix`

rebuilds the app’s frontend assets (JS and CSS) and generates updated bundled files.

Browsers cache static assets for performance. After modifying JavaScript files, the browser may still load the old cached version. Rebuilding creates new asset versions, ensuring the browser loads the updated files.

This process is called cache-busting and ensures recent JS changes are reflected properly.

### Difference Between Jinja Context
### Print Format Context

## In Print Formats:

The variable doc is automatically available.

It represents the current document being printed.

No need to manually define context.

Used for generating PDFs or printed documents.

Web Page Context

## In Web Pages:

No variables are automatically available.

Data must be manually passed using get_context(context) in Python.

Used for website or portal pages.

Fully controlled by the developer.

## override_whitelisted_methods vs Monkey Patching

### override_whitelisted_methods

`override_whitelisted_methods` is a Frappe hook used to replace a whitelisted method from another app without modifying the original source code. The override is declared in `hooks.py`, making the behavior explicit and easy to track. Because it is managed by the Frappe framework, it is upgrade-safe and reversible by simply removing the hook.


### Monkey Patching

Monkey patching means replacing a function dynamically at runtime by reassigning it in code.

## What Happens if Two Apps Override the Same Method?

If two apps register an override for the same whitelisted method using `override_whitelisted_methods`, Frappe loads them based on the order defined in `sites/apps.txt`. The override from the **last loaded app takes precedence** and becomes the active implementation.

The earlier override is silently replaced. This means only one override can be active at a time, which may create conflicts in multi-app environments.

---

## Signature Mismatch and TypeError

When overriding a method, the override function must have the **same function signature** as the original method. If the parameters do not match, the framework may pass arguments that the function cannot accept.

Original method example:

```python
def get_count(doctype, filters=None, debug=False, cache=False):
```

Correct override:

```python
def custom_get_count(doctype, filters=None, debug=False, cache=False):
```

If the override does not accept the same arguments, Python raises a `TypeError`.

Example incorrect override:

```python
def custom_get_count(doctype):
```

When Frappe calls the function with additional parameters, the following error occurs:

```
TypeError: custom_get_count() takes 1 positional argument but 4 were given
```

This happens when:

* Required parameters are missing
* Argument order is incorrect
* The function cannot accept additional parameters passed by the framework

To avoid future compatibility issues, it is sometimes recommended to include `**kwargs` in the override function so that extra parameters can be handled safely.

