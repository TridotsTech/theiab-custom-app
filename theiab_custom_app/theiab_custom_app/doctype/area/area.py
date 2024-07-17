# Copyright (c) 2024, info@tridotstech.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Area(Document):
	def before_save(self):
		if not frappe.db.get_all("Zone", filters = {"zone_code":self.area_code}, fields = ["name"]):
			if frappe.db.get_value("Warehouse",{"warehouse_code":self.zone}, "name"):
				company = frappe.db.get_value("User Permission", {"user":frappe.session.user, "allow":"Company"}, "for_value") or frappe.db.get_value("Global Defaults", "Global Defaults", "default_company")
				new_warehouse = frappe.get_doc({
												"doctype":"Warehouse",
												"company":company,
												"warehouse_name":self.area_name,
												"warehouse_code":self.area_code,
												"parent_warehouse":frappe.db.get_value("Warehouse",{"warehouse_code":self.zone}, "name"),
												"is_group":1
											}).insert(ignore_permissions = True)
				new_warehouse.save(ignore_permissions = True)
				frappe.db.commit()
			else:
				frappe.throw("Couldn't find Warehouse code in <b>Warehouse</b> !")
		else:
			frappe.throw("Area Code already exists !")
