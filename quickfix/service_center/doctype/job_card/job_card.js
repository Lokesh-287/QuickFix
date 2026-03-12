// Copyright (c) 2026, laptops, and tablets. Currently, everything runs on paper and WhatsApp. You will build their and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
        onload(frm) {
        frappe.realtime.on("job_ready", function(data) {
            
            frappe.show_alert({
                message: "Job is ready for delivery!",
                indicator: "green"
            });

        });

    },setup(frm){
        frm.set_query("assigned_technician",()=>{
            return {
                filters:{
                    status:"Active",
                    specialization:frm.doc.device_type
                }
            }
        })
    },
	refresh(frm) {
        if (!frappe.user.has_role("System Manager")) {
            frm.set_df_property("customer_phone", "hidden", 1);
        }
        if (frm.doc.status) {

            let color = "gray";

            if (frm.doc.status === "Draft") {
                color = "gray";
            }
            else if (frm.doc.status === "Pending Diagnosis") {
                color = "orange";
            }
            else if (frm.doc.status === "Awaiting Customer Approval") {
                color = "yellow";
            }
            else if (frm.doc.status === "In Repair") {
                color = "blue";
            }
            else if (frm.doc.status === "Ready for Delivery") {
                color = "green";
            }
            else if (frm.doc.status === "Delivered") {
                color = "darkgreen";
            }
            else if (frm.doc.status === "Cancelled") {
                color = "red";
            }
            frm.page.set_indicator(frm.doc.status, color);
            frm.dashboard.clear_headline();
            frm.dashboard.add_indicator(frm.doc.status, color);
        }
        if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1){
            frm.add_custom_button("Mark as Delivered",()=>{
                frappe.call({
                    method:"quickfix.api.mark_as_delivered",
                    args:{
                        job_card:frm.doc.name
                    },callback:function(){
                        frm.reload_doc();
                    }
                })
            })
        }
        if (frappe.boot.quickfix_shop_name) {

            frm.page.set_indicator(
                frappe.boot.quickfix_shop_name,
                "blue"
            );

        }
	},
    assigned_technician(frm) {
        console.log("!!!!!!!!!!!!!!!!!!")
        if (frm.doc.assigned_technician) {
            console.log(frm.doc.assigned_technician)
            frappe.db.get_value(
                "Technician",
                frm.doc.assigned_technician,
                "specialization",
                function(r) {

                    if (r.specialization && r.specialization !== frm.doc.device_type) {

                        frappe.msgprint({
                            title: "Specialization Mismatch",
                            message: "Selected technician specialization does not match the device type.",
                            indicator: "orange"
                        });

                    }

                }
            );

        }

    }
    
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
