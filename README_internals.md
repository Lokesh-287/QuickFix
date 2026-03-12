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

## J2 - Raw Print vs HTML to PDF

### Difference between Raw Printing and HTML-PDF via WeasyPrint

**Raw Printing (ESC/POS):**
Raw printing sends binary ESC/POS commands directly to a thermal
printer over USB, serial, or network. The printer interprets these
commands itself — there is no HTML, no CSS, no browser involved.
Example command: ESC @ resets the printer, ESC E 1 enables bold.
This is used for 80mm receipt printers in shops and restaurants.
Frappe does not natively support ESC/POS — you would need a
separate service (like a local print server or browser extension)
to bridge Frappe's output to the printer.

**HTML-PDF via WeasyPrint:**
Frappe renders the Jinja template to HTML on the server, then
passes that HTML to WeasyPrint which converts it to a PDF file.
WeasyPrint is a Python library that implements a subset of CSS —
it does NOT use a browser engine. The PDF is then sent to the
browser for download or printing via the browser's print dialog.

Key difference: Raw printing talks directly to hardware.
WeasyPrint produces a PDF file from HTML/CSS on the server.

---

### 3 CSS properties that work in browser but fail in WeasyPrint

1. **CSS Grid (`display: grid`)**
   WeasyPrint has very limited or no support for CSS Grid.
   Use `display: table` or `<table>` elements instead.

2. **`position: fixed`**
   Fixed positioning is ignored in WeasyPrint — elements do not
   stay in place relative to the page. Use `@page` margins for
   headers/footers instead.

3. **CSS Flexbox (`display: flex`)**
   Flexbox support in WeasyPrint is partial and unreliable.
   Complex flex layouts break silently — use tables instead.

---

### format_value() — with vs without

**Without format_value (raw value):**
{{ doc.final_amount }}
Output: 13100.0
Problem: No currency symbol, no thousands separator,
shows raw float — looks unprofessional and confusing.

**With get_formatted() (correct):**
{{ doc.get_formatted("final_amount") }}
Output: ₹ 13,100.00
Correct: Currency symbol, thousands separator, 2 decimal places,
respects the system currency settings.

This is why every numeric Currency field in a print format
must use get_formatted() — never output raw float values.

## K1 - Background Jobs

### Task A — The 3 Queue Names

**short queue:**
For fast tasks that complete in under 5 minutes.
Examples: sending a single email, sending a webhook,
publishing a small notification.
Why separate: a short email task must not sit behind a
30-minute report generation job. Short queue workers
pick up only short queue jobs — guaranteed fast execution.

**default queue:**
For medium tasks that complete in 5–15 minutes.
Examples: processing a batch of records, generating
a small report, syncing data with an external API.
This is the queue used when no queue is specified.

**long queue:**
For heavy tasks that can take 15 minutes or more.
Examples: monthly revenue reports, bulk data migrations,
large file processing, sending 1000 emails.
timeout=600 or higher. If you put a heavy job in the
short queue, it will block all short tasks behind it.

## K2 - Scheduler Events & Cron

### How to disable scheduler for a specific site

Option 1 — via bench command:
bench --site quickfix-dev.localhost scheduler disable

Option 2 — via site_config.json:
{
    "pause_scheduler": 1
}

To re-enable:
bench --site quickfix-dev.localhost scheduler enable

Or remove pause_scheduler from site_config.json.

### Why disable scheduler on a dev site?

1. Prevent accidental emails — daily jobs like low stock
   alerts or job ready emails would fire for real during
   development, sending emails to real customers or managers.

2. Prevent duplicate data — scheduled jobs that insert
   records (Audit Log entries, revenue reports) would
   create noise in your dev database making it hard to
   test cleanly.

3. Prevent stock changes — any scheduled job that modifies
   inventory or financial data would corrupt your test data.

4. Performance — scheduler adds background load. On a
   dev machine you want all resources for active development,
   not background jobs.

Rule of thumb: always disable scheduler on dev sites
unless you are specifically testing scheduler behavior.

### What happens to scheduled jobs when worker was down?

Short answer: MISSED jobs do NOT run when worker comes back.

Detailed explanation:
- Frappe's scheduler runs on a heartbeat — it checks every
  minute if any scheduled job is due
- If the worker process was down for 2 hours and a daily
  job was scheduled during that time, the scheduler will
  NOT retroactively run it when the worker restarts
- The scheduler only asks "is this job due RIGHT NOW?"
  not "was this job missed while I was down?"
- This means: if your worker crashed at 1am and restarted
  at 3am, and your monthly report was scheduled for 2am,
  it will NOT run until next month at 2am

Exception: if the job was already enqueued in Redis before
the worker went down, it WILL run when the worker comes
back — because it's sitting in the Redis queue waiting.
But if the scheduler never got to enqueue it, it is missed.


### K3

## Task 1

# Fix for N+1 Query Problem

## Approach A · JOIN in `get_all()` — Best for simple field reads
```python
# FIXED — single query with JOIN (dot-notation)
job_cards = frappe.get_all(
    "Job Card",
    fields=[
        "name",
        "assigned_technician",
        "assigned_technician.technician_name",   # dot-notation JOIN
        "assigned_technician.phone"
    ]
)

for jc in job_cards:
    print(jc.technician_name, jc.phone)
```

**Result:** 1 SQL query total — no matter how many job cards exist.

---

## Approach B · Batch fetch + in-memory lookup — ⭐ Best when you need full documents

```python
# FIXED — bulk fetch + dict lookup
job_cards = frappe.get_all(
    "Job Card",
    fields=["name", "assigned_technician"]
)

# Step 1 — collect unique technician IDs
tech_ids = list({jc.assigned_technician for jc in job_cards})

# Step 2 — ONE batch query for all technicians
technicians = frappe.get_all(
    "Technician",
    filters=[["name", "in", tech_ids]],
    fields=["name", "technician_name", "phone"]
)

# Step 3 — build O(1) lookup dict
tech_map = {t.name: t for t in technicians}

# Step 4 — loop with ZERO additional DB calls
for jc in job_cards:
    tech = tech_map.get(jc.assigned_technician)
    if tech:
        print(tech.technician_name, tech.phone)
```

**Result:** 2 SQL queries total regardless of dataset size.

###  K3  Task C - Indexing: Why Not Add a Search Index to Every Field?

Adding an index helps **read/search queries run faster**, but adding indexes to every field can hurt performance.

**1. Slower Insert/Update/Delete**
Whenever data is added, updated, or deleted, the database must also update all related indexes.
If there are too many indexes, these operations become slower.

**2. More Storage Usage**
Each index takes extra disk space. Creating indexes on many fields increases the database size unnecessarily.

**3. Higher Maintenance Cost**
Indexes need to be maintained and updated. Too many indexes increase database maintenance work.

**Conclusion**
Indexes should only be added to fields that are **frequently used in filtering, searching, joins, or sorting**. Over-indexing wastes storage and slows down write operations.

### Task D – Report Performance Profiling

SQL logging was enabled in **site_config.json** by setting the logging level to **DEBUG**. This allowed the bench console to show detailed logs when the **Technician Performance Report** was executed.

After running the report, the console logs were inspected to see the queries executed. The report fetches data from the **Job Card** table using filters, including the **creation date**.

The slowest operation was the query filtering Job Cards by the `creation` date because, without an index, the database may perform a **full table scan**.

To improve performance, an **index was added to the `creation` field**. This allows the database to quickly find records within the date range, which improves the report execution speed.

Here it is — headings and actual request/response only, no explanations:

---

## L1 – Task A: REST Resource API

---

### 1. GET – List Job Cards

```
GET http://quickfix-dev.localhost:8000/api/resource/Job%20Card
```

```json
{
    "data": [
        { "name": "JC-2026-00041" },
        { "name": "JC-2026-00042" },
        { "name": "JC-2026-00043" },
        { "name": "JC-2026-00051" },
        { "name": "JC-2026-00052" },
        { "name": "JC-2026-00053" },
        { "name": "JC-2026-00054" },
        { "name": "JC-2026-00055" },
        { "name": "JC-2026-00056" },
        { "name": "JC-2026-00057" },
        { "name": "JC-2026-00058" },
        { "name": "JC-2026-00059" },
        { "name": "JC-2026-00060" },
        { "name": "JC-2026-00061" },
        { "name": "JC-2026-00062" },
        { "name": "JC-2026-00063" },
        { "name": "JC-2026-00064" },
        { "name": "JC-2026-00065" },
        { "name": "JC-2026-00066" },
        { "name": "JC-2026-00067" }
    ]
}
```

---

### 2. GET – Single Job Card

```
GET http://quickfix-dev.localhost:8000/api/resource/Job%20Card/JC-2026-00072
```

```json
{
    "data": {
        "name": "JC-2026-00072",
        "owner": "Administrator",
        "creation": "2026-03-06 14:46:35.472304",
        "modified": "2026-03-06 14:46:35.472304",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "customer_name": "Customer 22",
        "customer_phone": "8219992658",
        "device_type": "Tablet",
        "device_model": "Model-846",
        "problem_description": "Auto generated repair issue",
        "assigned_technician": "TECH-0001",
        "estimated_cost": 0.0,
        "priority": "Normal",
        "parts_total": 17200.0,
        "labour_charge": 500.0,
        "final_amount": 17700.0,
        "payment_status": "Paid",
        "status": "Awaiting Customer Approval",
        "doctype": "Job Card",
        "parts_used": [
            {
                "name": "4k283edacs",
                "idx": 1,
                "part": "RAM002-PART-2026-0030",
                "part_name": "Laptop RAM 16GB",
                "unit_price": 5000.0,
                "quantity": 2.0,
                "total_price": 10000.0,
                "parent": "JC-2026-00072",
                "parentfield": "parts_used",
                "parenttype": "Job Card",
                "doctype": "Part Usage Entry"
            },
            {
                "name": "4k2bq4o3hp",
                "idx": 2,
                "part": "SSD002-PART-2026-0017",
                "part_name": "Laptop SSD 512GB",
                "unit_price": 6000.0,
                "quantity": 1.0,
                "total_price": 6000.0,
                "parent": "JC-2026-00072",
                "parentfield": "parts_used",
                "parenttype": "Job Card",
                "doctype": "Part Usage Entry"
            },
            {
                "name": "4k2cueq0e1",
                "idx": 3,
                "part": "SPK001-PART-2026-0009",
                "part_name": "Speaker",
                "unit_price": 400.0,
                "quantity": 3.0,
                "total_price": 1200.0,
                "parent": "JC-2026-00072",
                "parentfield": "parts_used",
                "parenttype": "Job Card",
                "doctype": "Part Usage Entry"
            }
        ]
    }
}
```

---

### 3. POST – Create a Spare Part

```
POST http://quickfix-dev.localhost:8000/api/resource/Spare%20Part
```

```json
{
    "part_name":     "Laptop Battery",
    "part_code":     "BAT001",
    "unit_cost":     800,
    "selling_price": 1200,
    "stock_qty":     10
}
```

```json
{
    "data": {
        "name": "BAT001-PART-2026-0031",
        "owner": "Administrator",
        "creation": "2026-03-11 11:35:32.092501",
        "modified": "2026-03-11 11:35:32.092501",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "part_name": "Laptop Battery",
        "part_code": "BAT001",
        "unit_cost": 800.0,
        "selling_price": 1200.0,
        "stock_qty": 10.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    }
}
```

---

### 4. PUT – Update a Spare Part

```
PUT http://quickfix-dev.localhost:8000/api/resource/Spare%20Part/RAM002-PART-2026-0030
```

```json
{
    "selling_price": 15000
}
```

```json
{
    "data": {
        "name": "RAM002-PART-2026-0030",
        "owner": "Administrator",
        "creation": "2026-03-06 13:25:28.066013",
        "modified": "2026-03-11 11:40:29.242413",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "part_name": "Laptop RAM 16GB",
        "part_code": "RAM002",
        "compatible_device_type": "Laptop",
        "unit_cost": 3500.0,
        "selling_price": 15000.0,
        "stock_qty": 5.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    },
    "_server_messages": "[\"{\\\"message\\\": \\\"Stock below threshold\\\", \\\"title\\\": \\\"Message\\\"}\"]"
}
```

---

### 5. DELETE – Delete a Spare Part

```
DELETE http://quickfix-dev.localhost:8000/api/resource/Spare%20Part/BAT001-PART-2026-0031
```

```json
{
    "data": "ok"
}
```
### Task B 


### Difference between Session Cookie Authentication and Token Authentication
Session Cookie Authentication:
- Requires login using `/api/method/login`
- Returns a session cookie (`sid`)
- Browser stores and automatically sends the cookie
- Used mainly for **browser-based applications** like Frappe Desk.
Token Authentication:
- Uses **API Key and API Secret**
- Sent in request header: `Authorization: token api_key:api_secret`
- Does not require login session
- Used mainly for **server-to-server communication**, scripts, or external integrations.
---
### Appropriate UsageBrowser Applications → Session Cookie Authentication
Server-to-Server APIs → Token Authentication

### Task C - Custom Whitelisted Method

A whitelisted method `get_job_summary` was created in `api.py`.
It reads `job_card_name` using `frappe.form_dict` and returns only selected fields (job_card, status, technician, created_date).
Sensitive fields like `customer_email` are not returned.
If the job card does not exist, it returns `{"error": "Not found"}` with HTTP 404.
The Python date object is automatically serialized by Frappe to JSON format (e.g., `"2026-03-06"`).
After modifying a DocType (for example changing a field label), users may still see old values because DocType metadata is cached.

### Task D – Rate Limiting & Abuse Protection

The `get_job_by_phone` API uses `allow_guest=True`, so a rate limiter was implemented using `frappe.cache`.
Requests are tracked per **IP address per minute**, and if the number exceeds the limit, the API returns **HTTP 429 (Too Many Requests)**.

Risks of `allow_guest=True` endpoints:

1. **Brute force attacks** – attackers can try many phone numbers to access data.
2. **API abuse / DoS** – sending large numbers of requests can overload the server.
3. **Data scraping** – attackers may automatically collect large amounts of data from the API.

## M1 – Server Script DocType

### Blocked Python functions/modules in Server Script sandbox

Server Scripts run inside a restricted sandbox environment in Frappe. Dangerous Python modules and functions are blocked for security reasons.

Examples of blocked modules/functions:
- os module (cannot access operating system commands)
- subprocess module (cannot run system processes)
- sys module (restricted system access)
- open() file operations (cannot read/write files on the server)
- eval() and exec() for arbitrary code execution

These restrictions prevent server scripts from executing unsafe operations or accessing the system environment.

---

### Three things you CANNOT do in a Server Script but can do in App Code

1. Access the file system using open(), os, or file operations.
2. Import and use arbitrary Python libraries or external packages.
3. Execute system-level commands using subprocess or os.system().

These operations are only possible in full app code where there are no sandbox restrictions.

---

### Two scenarios where Server Scripts are acceptable

1. Implementing simple business rules such as automatically updating a field value when a condition is met.
2. Creating lightweight API endpoints for simple data retrieval or quick automation.

Server Scripts are useful for quick customizations without modifying the application code.

---

### Two scenarios where App Code should be used instead

1. Complex business logic or workflows involving multiple operations.
2. Integrations with external systems or APIs requiring authentication or background processing.

These cases require proper application code for reliability and maintainability.

---

### Governance and Maintainability Risks of Server Scripts

Server Scripts are stored in the database rather than version-controlled files. This creates governance risks such as:

- Changes not being tracked in Git.
- Difficult migration between development, staging, and production environments.
- Harder code review and auditing.
- Risk of hidden logic affecting system behavior.

For long-term maintainability, important logic should be implemented in application code rather than server scripts.


### M2 - Caching, Redis & Cache Invalidation
## Task A


## 5 Things Frappe Caches in Redis

**1. bootinfo**
Stored as a Redis Hash (`frappe.cache.hget("bootinfo", "Administrator")`). Contains the full desk startup payload — user roles, permission sets (can_create, can_read, can_write, can_submit, can_cancel, can_delete), system defaults, workspaces, reports, letter heads, and app versions. Built once per user per session. Invalidated by `frappe.clear_cache()` or logout.

**2. DocType metadata / meta**
Keys: `doctype_meta`, `metadata_version`. Stores the serialised meta object for every DocType — field definitions, naming series, controller path, and permission rules. Frappe reads this instead of querying `tabDocType` on every form open. `metadata_version` is bumped on every `bench migrate` or DocType save to signal workers to drop their local cache.

**3. Website context**
Keys: `document_cache::Workspace::QuickFix`, `document_cache::Workspace::Build`, `document_cache::Website Theme::Standard`. Stores serialised Workspace layouts, Website Theme, and portal settings. Read on every desk page load to render the sidebar and shortcuts. Invalidated when the document is saved.

**4. Translations**
Keys: `lang_user_translations`, `merged_translations`. `lang_user_translations` holds custom Translation records. `merged_translations` is the final merged dict — Frappe core strings + app strings + user overrides for the active language. The `__messages` dict inside bootinfo is the browser copy of this cache. Invalidated when a Translation record is saved.

**5. User permissions**
Keys: `roles`, `domain_restricted_doctypes`, `_user_settings`. `roles` caches all Role names so Frappe never hits `tabRole` on every request. `domain_restricted_doctypes` caches which DocTypes are hidden per active domain. `_user_settings` stores per-user column preferences and saved filters. Invalidated by role changes or `frappe.clear_cache()`.

### Task B - Custom cache with expiry + invalidation:

Using Redis caching improves performance by reducing database queries for frequently accessed dashboard data. However, without proper cache invalidation, users may see stale data. Implementing cache invalidation using DocType events ensures that the UI always displays up-to-date information.

## Task C – Debugging Stale UI

### Stale JavaScript after a change

Sometimes after modifying a JavaScript file, the browser may still load the old version because Frappe caches built assets.

To rebuild assets and load the latest JS:

```
bench build --app quickfix
```

`bench build --app quickfix` rebuilds the JavaScript and CSS files for the **quickfix** app so the browser loads the updated code.

---

### Stale DocType Metadata

After modifying a DocType (for example changing a field label), users may still see old values because DocType metadata is cached.

To clear this metadata cache:

```
bench clear-cache
```

This command clears the server cache and reloads updated DocType metadata such as field labels, properties, and permissions.



# L2 Payment Webhook – Internal Notes

## Endpoint

Webhook endpoint to receive payment confirmations from the payment gateway:

/api/method/quickfix.api.payment_webhook

The method uses `@frappe.whitelist(allow_guest=True)` so external systems can call it without authentication.

## HMAC Signature Verification

The webhook validates the request using **HMAC SHA256**.
The gateway sends an `X-Signature` header, and the server generates the expected signature using a shared secret from `site_config.json`.

`hmac.compare_digest()` is used instead of `==` to prevent **timing attacks**, ensuring constant-time comparison of signatures.

## Deduplication

Payment gateways may resend the same webhook event.
The system checks the **Audit Log** table for an existing entry (`action = payment_received`, `document_name = ref`).
If found, the request is marked as **duplicate** and skipped.

## Result

This ensures:

* Secure webhook verification
* Protection from replay or duplicate events
* Safe update of Job Card payment status
* Audit logging for traceability

