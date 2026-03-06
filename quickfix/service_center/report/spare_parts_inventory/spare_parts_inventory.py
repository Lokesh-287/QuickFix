# Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
# For license information, please see license.txt

import frappe


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_report_summary(data)
    return columns, data, None, None, summary

def get_columns():
    return [
        {"label": "Part Name", "fieldname": "part_name", "fieldtype": "Data", "width": 180},
        {"label": "Part Code", "fieldname": "part_code", "fieldtype": "Data", "width": 120},
        {"label": "Device Type", "fieldname": "compatible_device_type", "fieldtype": "Link", "options": "Device Type", "width": 130},
        {"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
        {"label": "Reorder Level", "fieldname": "reorder_level", "fieldtype": "Float", "width": 120},
        {"label": "Unit Cost", "fieldname": "unit_cost", "fieldtype": "Currency", "width": 120},
        {"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 120},
        {"label": "Margin %", "fieldname": "margin_pct", "fieldtype": "Percent", "width": 100},
    ]

def get_data(filters):
    parts = frappe.get_list(
        "Spare Part",
        fields=["part_name", "part_code", "compatible_device_type",
                "stock_qty", "reorder_level", "unit_cost", "selling_price"],
        filters={"is_active": 1},
        order_by="part_name asc"
    )

    data = []
    total_stock_qty = 0
    total_value = 0

    for p in parts:
        if p.selling_price and p.unit_cost and p.unit_cost > 0:
            margin = ((p.selling_price - p.unit_cost) / p.unit_cost) * 100
        else:
            margin = 0

        row = {
            "part_name": p.part_name,
            "part_code": p.part_code,
            "compatible_device_type": p.compatible_device_type,
            "stock_qty": p.stock_qty,
            "reorder_level": p.reorder_level,
            "unit_cost": p.unit_cost,
            "selling_price": p.selling_price,
            "margin_pct": round(margin, 2),
        }
        data.append(row)
        total_stock_qty += p.stock_qty or 0
        total_value += (p.stock_qty or 0) * (p.unit_cost or 0)

    # Total row
    data.append({
        "part_name": "<b>Total</b>",
        "part_code": "",
        "compatible_device_type": "",
        "stock_qty": total_stock_qty,
        "reorder_level": "",
        "unit_cost": "",
        "selling_price": "",
        "margin_pct": total_value,  # reuse margin col for total value in total row
    })

    return data

def get_report_summary(data):
    # Exclude the total row
    parts = [r for r in data if r.get("part_name") != "<b>Total</b>"]
    total_parts = len(parts)
    below_reorder = sum(
        1 for p in parts
        if (p.get("stock_qty") or 0) <= (p.get("reorder_level") or 0)
    )
    total_value = sum(
        (p.get("stock_qty") or 0) * (p.get("unit_cost") or 0)
        for p in parts
    )

    return [
        {"label": _("Total Parts"), "value": total_parts, "indicator": "Blue"},
        {"label": _("Below Reorder"), "value": below_reorder, "indicator": "Red" if below_reorder else "Green"},
        {"label": _("Total Inventory Value"), "value": total_value, "datatype": "Currency", "indicator": "Blue"},
    ]