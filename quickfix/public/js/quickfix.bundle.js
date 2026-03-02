// frappe.provide("frappe.views");
///home/lokesh2/frappe-bench/apps/quickfix/quickfix/public/js/quickfix.bundle.js
console.log("23456789999999 test ")

setTimeout(() => {
//    frappe.after_ajax(() => {

    if (frappe.boot.quickfix_shop_name) {
        console.log(frappe.boot.quickfix_shop_name)
        $(".navbar-home").append(`
            <span style="margin-left:15px;font-weight:bold;">
                 ${frappe.boot.quickfix_shop_name}
            </span>
        `);

    }

// });
}, 100);