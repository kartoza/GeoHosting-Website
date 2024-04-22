# Copyright (c) 2024, tinashe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus


class GeohostingMembership(Document):
	
	def before_submit(self):
		exists = frappe.db.exists(
			"Geohosting Membership",{
				"geohosting_member": self.geohosting_member,
				"docstatus": DocStatus.submitted(),
				# check if the to date is later
				"to_date": (">", self.from_date)
			}
		)
		if exists:
			frappe.throw("There is an active membership for this member")
