console.log("QuickFixxxxx JS Loaded");





///home/lokesh2/frappe-bench/apps/quickfix/quickfix/public/js/quickfix.js

console.log("QuickFix JS Loaded");
setTimeout(() => {
    console.log("2345678")
        console.log(frappe.boot.quickfix_shop_name)

    if (frappe.boot.quickfix_shop_name) {

    $(".navbar-home").append(
        `<span style="margin-left:15px;">
            ${frappe.boot.quickfix_shop_name}
        </span>
        <span>Testtt</span>`
    );
}
}, 5000);
    





