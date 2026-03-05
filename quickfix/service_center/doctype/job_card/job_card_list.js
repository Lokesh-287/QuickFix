frappe.listview_settings['Job Card'] = {

    add_fields: ["status","final_amount", "priority"],
    has_indicator_for_draft:true,

    get_indicator(doc) {

        if (doc.status === "Pending Diagnosis") {
            return [("Pending Diagnosis"), "orange", "status,=,Pending Diagnosis"];
        }

        if (doc.status === "Awaiting Customer Approval") {
            return [("Awaiting Customer Approval"), "yellow", "status,=,Awaiting Customer Approval"];
        }

        if (doc.status === "In Repair") {
            return [("In Repair"), "blue", "status,=,In Repair"];
        }

        if (doc.status === "Ready for Delivery") {
            return [("Ready for Delivery"), "green", "status,=,Ready for Delivery"];
        }

        if (doc.status === "Delivered") {
            return [("Delivered"), "gray", "status,=,Delivered"];
        }

        if (doc.status === "Cancelled") {
            return [("Cancelled"), "red", "status,=,Cancelled"];
        }

    },
     formatters: {
        final_amount(value) {
            if (!value) return value;
            return `<b style="color:green">₹ ${value}</b>`;
        }
    },
    button: {
        show(doc) {
            return doc.status === "In Repair";
        },

        get_label() {
            return __("Complete");
        },

        get_description(doc) {
            return __("Mark {0} as Ready for Delivery", [doc.name]);
        },

        action(doc) {
            frappe.call({
                method: "quickfix.api.mark_ready",
                args: {
                    job_card: doc.name
                },
                callback() {
                    frappe.show_alert({
                        message: "Job marked Ready for Delivery",
                        indicator: "green"
                    });
                    frappe.listview.refresh();
                }
            });

        }
    }

};