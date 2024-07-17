# Copyright (c) 2024, info@tridotstech.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Outlet(Document):
	def before_save(self):
		if not frappe.db.get_all("Area", filters = {"area_code":self.outlet_code}, fields = ["name"]) and not frappe.db.get_all("Zone", filters = {"zone_code":self.outlet_code}, fields = ["name"]):
			if frappe.db.get_value("Warehouse",{"warehouse_code":self.area}, "name"):
				company = frappe.db.get_value("User Permission", {"user":frappe.session.user, "allow":"Company"}, "for_value") or frappe.db.get_value("Global Defaults", "Global Defaults", "default_company")
				new_warehouse = frappe.get_doc({
												"doctype":"Warehouse",
												"company":company,
												"warehouse_name":self.outlet_name,
												"warehouse_code":self.outlet_code,
												"parent_warehouse":frappe.db.get_value("Warehouse",{"warehouse_code":self.area}, "name"),
												"is_group":0
											}).insert(ignore_permissions = True)
				new_warehouse.save(ignore_permissions = True)
				frappe.db.commit()
			else:
				frappe.throw("Couldn't find Warehouse code in <b>Warehouse</b> !")
		else:
			frappe.throw("Outlet Code already exists !")
