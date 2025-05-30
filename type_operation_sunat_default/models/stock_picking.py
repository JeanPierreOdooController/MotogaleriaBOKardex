# -*- encoding: utf-8 -*-
from odoo import models, api,fields

class StockPicking(models.Model):
	_inherit='stock.picking'

	
	type_operation_sunat_id = fields.Many2one('type.operation.kardex', string='Tipo de Operacion sunat')


	@api.model
	def create(self, vals):
		res = super(StockPicking, self).create(vals)
		res.put_sunattype()
		return res

	def write(self, vals):
		res = super(StockPicking,self).write(vals)
		if "location_id" in vals or "location_dest_id" in vals:
			for i in self:
				i.put_sunattype()
		return res

#location_id default va en false en ciertos casos
#	@api.model
#	def default_get(self, fields):
#		res = super(stock_picking, self).default_get(fields)
#		type_kardex=False
#		if "location_id" in res and "location_dest_id" in res:
#			location_id = self.env["stock.location"].sudo().search([("id","=",res["location_id"])])
#			location_dest = self.env["stock.location"].sudo().search([("id","=",res["location_dest_id"])])
#			if location_id.usage == "internal" and location_dest.usage == "supplier":
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%06%")],limit=1).id
#			elif location_id.usage == "customer" and location_dest.usage == "internal":
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%05%")],limit=1).id
#			elif location_id.usage == "supplier" and location_dest.usage == "internal":
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%02%")],limit=1).id
#			elif location_id.usage == "internal" and location_dest.usage == "customer":
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%01%")],limit=1).id
#			elif (location_id.usage == "internal"  and location_dest.usage == "internal") or (location_id.usage == "internal"  and location_dest.usage == "transit"):
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%11%")],limit=1).id
#			elif location_id.usage == "transit" and location_dest.usage == "internal":
#				type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%21%")],limit=1).id
#		if type_kardex!=False:
#			res["type_operation_sunat_id"]=type_kardex
#		return res

	def put_sunattype(self):
		for i in self:
			type_kardex = False
			if not i.type_operation_sunat_id.id and i.location_id.id and i.location_dest_id.id:
				location_id = i.location_id
				location_dest = i.location_dest_id
				if location_id.usage == "internal" and location_dest.usage == "supplier":
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%06%")],limit=1).id
				elif location_id.usage == "customer" and location_dest.usage == "internal":
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%05%")],limit=1).id
				elif location_id.usage == "supplier" and location_dest.usage == "internal":
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%02%")],limit=1).id
				elif location_id.usage == "internal" and location_dest.usage == "customer":
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%01%")],limit=1).id
				elif (location_id.usage == "internal"  and location_dest.usage == "internal") or (location_id.usage == "internal"  and location_dest.usage == "transit"):
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%11%")],limit=1).id
				elif location_id.usage == "transit" and location_dest.usage == "internal":
					type_kardex = self.env["type.operation.kardex"].sudo().search([("code","like","%21%")],limit=1).id
				if type_kardex!=False:
					i.type_operation_sunat_id = type_kardex



