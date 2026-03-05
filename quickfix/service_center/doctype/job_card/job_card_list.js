frappe.listview_settings['Job Card'] = {

    add_fields: ["status"],
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

    }

};