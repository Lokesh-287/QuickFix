frappe.dashboards.chart_sources["Status Chaart Data"] = {
    onload(){
        frappe.call({
    method: "quickfix.api.get_status_chart_data"
});
    }
};