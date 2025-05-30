# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'


	@api.model
	def create(self,vals):	
		res = super(SaleOrderLine,self).create(vals)
		res.verify_discount_no_cero()
		return res

	def verify_discount_no_cero(self):
		# Si viene del boton 'Actualizar Precios'
		if "permiso_canal" in self.env.context:
			return
		for i in self:
			if i.discount == 0:
				continue
			if not self.env.user.has_group("sale_discount_tarifa_group.sale_order_line_discount_group"):
				raise UserError("Campo Descuento solo puede ser modificada por el grupo 'Manejo Descuento En Ventas'")		

	def write(self,vals):
		res = super(SaleOrderLine,self).write(vals)
		# Si viene del boton 'Actualizar Precios'
		if "permiso_canal" in self.env.context:
			return res	
		# Si no modifica el descuento
		if not vals.get("discount",False):
			return res	
		if not self.env.user.has_group("sale_discount_tarifa_group.sale_order_line_discount_group"):
			raise UserError("Campo Descuento solo puede ser modificada por el grupo 'Manejo Descuento En Ventas'.")
		return res
