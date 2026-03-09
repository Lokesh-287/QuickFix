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




### Fieldname Collision Risk

A fieldname collision occurs when a custom field created in an app has the same **fieldname** as a field that may be added later by a future Frappe or ERPNext update. Since fieldnames must be unique within a DocType, this can lead to migration conflicts, duplicate field errors, or unexpected behavior during upgrades.
---

### Patching Order and Migration Stability

Frappe executes patches listed in `patches.txt` sequentially in the order they appear. If **Patch 1 creates a Custom Field** and **Patch 2 reads or modifies that field**, they must be separate entries so that Patch 1 runs first and ensures the field exists before Patch 2 uses it. If both operations are merged into a single patch or executed out of order, the system may fail because Patch 2 might try to access a field that has not yet been created, causing migration errors.

### H1 - Job Card Form Script (8 pts)

* The validate event should not rely on asynchronous server calls because the save process does not wait for them.

* Server-dependent validations should be implemented in backend Python methods.

* Asynchronous operations such as frappe.call are better suited for onload or refresh


## H3 Tree DocType

A **Tree DocType** in Frappe represents hierarchical data where records are organized in a parent–child structure instead of a flat list. It allows users to visualize and manage relationships between records in a tree format. Common examples include **Account (Chart of Accounts)** and **Employee hierarchy**, where nodes can have multiple child records.

## doctype_tree_js

`doctype_tree_js` is used to customize the behavior of a Tree DocType in the UI. It allows developers to add custom logic such as actions, filters, or UI behavior specific to the tree view.

## Required Fields for Tree DocType

A Tree DocType requires additional fields to maintain hierarchy:

* **parent_field** – stores the reference to the parent node in the hierarchy.
* **is_group** – indicates whether the node can contain children (`1` for group nodes, `0` for leaf nodes).

## H4 Client Script DocType vs Shipped JS

Frappe allows client-side customization either through the **Client Script DocType** or through **JavaScript files shipped inside an app**.

**Client Script DocType** stores JavaScript code in the database and applies it immediately without requiring deployment. This is useful for consultants or administrators who need to make quick UI changes directly from the Desk.

**Shipped JS files** are part of the application codebase (for example `job_card.js`). They are version-controlled and deployed with the app, making them more suitable for structured development and long-term maintenance.

### Tradeoffs

Client Scripts are convenient for quick changes but are harder to track and manage because they are stored in the database and not version controlled. Shipped JS files are better for production systems since they are properly version controlled and reviewed as part of the application code.

### Security Pitfall: Hiding Fields in JavaScript

In this customization, the field `customer_phone` is hidden for non-managers using JavaScript:

```javascript
frm.set_df_property("customer_phone", "hidden", 1);
```

However, this only hides the field in the **user interface** and does not prevent access to the data. The field can still be retrieved through an API request or server-side code.

For example:

```python
frappe.get_doc("Job Card", "JC-00001").customer_phone
```

This demonstrates that hiding fields in client-side JavaScript is **not a security mechanism**. Proper security must be enforced using role permissions or server-side validation.


### I1 – Query Report with SQL Safety


### SQL Injection Risk (Unsafe Method)

Using f-strings or string concatenation can cause SQL injection.

Example (unsafe):

```python
query = f"""
SELECT name FROM `tabJob Card`
WHERE device_type = '{device_type}'
"""
```

If a user enters malicious input like:

```
Mobile' OR 1=1 --
```

the query may return all records. This is called **SQL Injection**.

---

### Safe Parameterized Query

The report uses a **parameterized SQL pattern**:

```
%(device_type)s
```

Frappe safely substitutes the value when executing:

```python
frappe.db.sql(query, filters)
```

This prevents SQL injection and ensures safe database queries.

---
### Adding an Index on status

To ensure efficient filtering by status, an index was added in the Job Card DocType JSON by enabling the search_index property.

```
{
 "fieldname": "status",
 "fieldtype": "Select",
 "search_index": 1
}
```
This creates a database index on the status field in the tabJob Card table, improving query performance when filtering open job cards.

## I4 - Prepared Reports

### When to use Prepared Report vs real-time Script Report

Use Prepared Report when:
- Report takes more than 3-5 seconds (large datasets, complex aggregations)
- Data does not need to be real-time (yesterday's stats, monthly summaries)
- Multiple users run the same report — one cached result serves all of them

Use real-time Script Report when:
- Data must reflect current state (live stock levels, open job count right now)
- Filters vary per user making caching ineffective
- Report is fast enough to not block the user

### Staleness tradeoff

A Prepared Report is a snapshot taken at the moment the background job ran.
If 10 Job Cards are submitted after the report generated, those are invisible
to the user until someone triggers a new generation.

For a monthly revenue summary this is acceptable.
For a "current open jobs" count this is dangerous — use real-time instead.

### Caching risk

If underlying data changes between preparations, the user sees stale numbers
with no warning other than the "Last Generated" timestamp. A manager could
make staffing or financial decisions on hours-old data. Always document the
refresh schedule and display the generation time prominently.`

## I5 - Report Builder & Custom Report

### When is Report Builder appropriate?
- Simple flat list of a single DocType with no calculations
- Non-developer needs to create a report without writing code
- Report only needs filtering, sorting, and column selection
- Example: "All Job Cards for a customer" — just a filtered list, no math

### When must you use Script Report?
- Any aggregation is needed (SUM, COUNT, AVG)
- Data comes from multiple DocTypes
- Dynamic columns are needed (e.g. one column per Device Type)
- Custom chart or report_summary is required
- Permission-aware filtering via frappe.get_list is needed
- Any computed column (e.g. Margin %, Completion Rate)

### Scenario where Report Builder in production would be a mistake

A manager wants a "Revenue by Technician" report.
You build it in Report Builder because it looks like a simple Job Card list.

Report Builder cannot sum revenue per technician — it just lists
individual rows. The manager sees 500 rows instead of 10 technician
totals and draws wrong conclusions about who is performing best.

Worse — there is no error or warning. The report looks legitimate.
Financial decisions get made on meaningless raw data.

This is why any report involving business logic, calculations,
or summarization must be a Script Report — Report Builder is
only for simple lists, never for analytics. 

## J1 - Print Format

### How Frappe determines language when printing
Frappe checks in this order:
1. lang parameter in the print URL
2. Language set on the User record of the person printing
3. Default language in System Settings
Strings in {{ _("string") }} are looked up in the Translation
DocType for the resolved language and replaced at render time.

### Pattern 1 - frappe.get_all() directly in Jinja (BAD)
{{ frappe.get_all("Spare Part", fields=["part_name"]) }}
Runs a DB query on every single render. Cannot be cached.
Blocks PDF generation if query is slow. Hard to debug errors
inside Jinja context. Never do this.

### Pattern 2 - Pre-compute in before_print() (GOOD)
def before_print(self, settings=None):
    self.print_summary = f"{self.customer_name} - {self.device_brand}"

Then in template:
{{ doc.print_summary }}

Data fetched once in Python with full error handling.
Template only reads pre-attached values — zero DB calls.
Easy to unit test before_print() independently.
PDF generation is fast with no blocking queries.