// Copyright (c) 2024, info@tridotstech.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Requirement Entry", {
    refresh(frm) {
        if (frm.__islocal){
            frm.set_value("item_group", "");
        }
    },

    get_all_items: function(frm) {
        if (frm.doc.warehouse && frm.doc.item_group) {
            frappe.call({
                method: "theiab_custom_app.theiab_custom_app.doctype.requirements_entry.requirements_entry.get_data",
                args: {
                    warehouse: frm.doc.warehouse,
                    item_group: frm.doc.item_group
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("items");
                        r.message.forEach(function(item) {
                            let child = frm.add_child("items");
                            child.item_id = item.item_code
                            child.item_name = item.item_name
                            child.live_stock = item.live_stock
                        });
                        frm.refresh_field("items");
                    }
                }
            });
        } else {
            if (frm.item_group){
                frappe.throw("Please choose Outlet !");
            }
            if (frm.warehouse){
                frappe.throw("Please choose Item group !");
            }
        }
    }
});

