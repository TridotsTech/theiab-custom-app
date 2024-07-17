# Copyright (c) 2024, info@tridotstech.com and contributors
# For license information, please see license.txt

import frappe


from frappe.model.document import Document
from frappe.model.db_query import DatabaseQuery
from frappe.utils import cint, flt
from frappe.utils import today


class RequirementEntry(Document):
    def on_submit(self):
        if len(self.items) > 0:
            stock_entry_items = []
            warehouse = frappe.db.get_value("Warehouse",{"warehouse_code":self.warehouse}, "name")
            company = frappe.db.get_value("User Permission", {"user":frappe.session.user, "allow":"Company"}, "for_value") or frappe.db.get_value("Global Defaults", "Global Defaults", "default_company")
            company_details = frappe.get_doc("Company", company)
            stock_entry = frappe.get_doc({
                                            "doctype":"Material Request",
                                            "stock_entry_type":"Purchase",
                                            "company":company,
                                            "transaction_date":today(),
                                            "schedule_date":today(),
                                            "set_warehouse":warehouse,
                                            "cost_center":company_details.cost_center
                                        })
            
            for itm in self.items:
                if itm.required_quantity and itm.required_quantity > 0:
                    item_details = frappe.get_doc("Item", itm.item_id)
                    stock_entry_items.append({
                                                "doctype":"Material Request Item",
                                                "cost_center":company_details.cost_center,
                                                "item_code":itm.item_id,
                                                "item_name":itm.item_name,
                                                "qty":itm.required_quantity,
                                                "stock_uom":item_details.stock_uom,
                                                "parent":stock_entry.name
                                            })
            if stock_entry_items:
                stock_entry.update({
                                    "items": stock_entry_items,
                                    "docstatus":1
                                    })
                stock_entry.insert(ignore_permissions = True)
                stock_entry.save(ignore_permissions = True)
                frappe.db.commit()
            else:
                frappe.throw("Please enter the Required Quantity for any one Item !")



@frappe.whitelist()
def get_data(outlet = None, item_group = None):
    filters = []
    if outlet:
        warehouse = frappe.db.get_value("Warehouse",{"warehouse_code":outlet}, "name")
        filters.append(["warehouse", "=", warehouse])
    if item_group:
        lft, rgt = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"])
        items = frappe.db.sql_list(""" SELECT i.name 
                                         FROM `tabItem` i
                                        WHERE exists(SELECT name 
                                                    FROM `tabItem Group`
                                                    WHERE name = i.item_group 
                                                        AND lft >= %s AND rgt <= %s)
                                    """,(lft, rgt))
        filters.append(["item_code", "in", items])
    try:
        if DatabaseQuery("Warehouse", user = frappe.session.user).build_match_conditions():
            filters.append(["warehouse", "in", [w.name for w in frappe.get_list("Warehouse")]])
    except frappe.PermissionError:
        return []

    items = frappe.db.get_all(
                                 "Bin",
                                fields = ["item_code","actual_qty"],
                                filters = filters
                            )
    precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
    for item in items:
        item.update({
                        "item_name": frappe.db.get_value("Item", item.item_code, "item_name"),
                        "live_stock": flt(item.actual_qty, precision),
                    })
    return items