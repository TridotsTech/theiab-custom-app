# Copyright (c) 2024, info@tridotstech.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Zone(Document):
    def before_save(self):
        if not frappe.db.get_all("Outlet", filters = {"outlet_code":self.zone_code}, fields = ["name"]):
            company = frappe.db.get_value("User Permission", {"user":frappe.session.user, "allow":"Company"}, "for_value") or frappe.db.get_value("Global Defaults", "Global Defaults", "default_company")
            new_warehouse = frappe.get_doc({
                                            "doctype":"Warehouse",
                                            "company":company,
                                            "warehouse_name":self.zone_name,
                                            "warehouse_code":self.zone_code,
                                            "is_group":1
                                        }).insert(ignore_permissions = True)
            new_warehouse.save(ignore_permissions = True)
            frappe.db.commit()
        else:
            frappe.throw("Zone Code already exists !")