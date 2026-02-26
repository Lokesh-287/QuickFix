// Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	refresh(frm) {

	},
    
});

frappe.ui.form.on("Part Usage Entry",{
    quantity(frm,cdt,cdn){
        calculate_total_price(frm,cdt,cdn)
    },
    unit_price(frm,cdt,cdn){
        calculate_total_price(frm,cdt,cdn)
    },
    part_usage_entry_add(frm,cdt,cdn){
        calculate_total_price(frm,cdt,cdn)  
    }
})

function calculate_total_price(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    let total_price=(row.unit_price||0)*(row.quantity|| 0 )
    frappe.model.set_value(cdt,cdn,"total_price",total_price)
}
