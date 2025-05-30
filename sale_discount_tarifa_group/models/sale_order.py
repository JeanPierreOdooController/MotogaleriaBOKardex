# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	def action_update_prices(self):
		context=dict(self.env.context)
		context["permiso_canal"]=True
		# Actualizar el context si presiona el boton 'Actualizar Precios'
		res = super(SaleOrder,self.with_context(context)).action_update_prices()
		return res

	@api.model
	def create(self,vals):	
		res=super(SaleOrder,self).create(vals)
		res.verify_lista_precio_tarifa()
		return res

	def verify_lista_precio_tarifa(self):
		if "permiso_canal" in self.env.context:
			return
		for rec in self:
			# Si no existe la lista de precio o esta es igual a la del cliente
			if not rec.pricelist_id.id or rec.pricelist_id.id == rec.partner_id.property_product_pricelist.id:
				continue
			if not self.env.user.has_group("sale_discount_tarifa_group.sale_order_line_tarifa_group"):
					raise UserError("Campo Lista de Precios solo puede ser modificada por el grupo 'Manejo Lista de Precio Venta' ")

	def write(self,vals):
		res = super(SaleOrder,self).write(vals)
		# Si viene del boton 'Actualizar Precios' o si no no modifica la lista de precios
		if "permiso_canal" in self.env.context or vals.get("pricelist_id",False):
			return res
		for rec in self:
			# Si la lista de precios es igual a la del cliente
			if rec.pricelist_id.id == rec.partner_id.property_product_pricelist.id:
				continue
			if not rec.env.user.has_group("sale_discount_tarifa_group.sale_order_line_tarifa_group"):
				raise UserError("Campo Lista de Precios solo puede ser modificada por el grupo 'Manejo Lista de Precio Venta' ")
		return res



