# -*- encoding: utf-8 -*-
from odoo import models, api

class sale_order(models.Model):
	_inherit='sale.order'

	def action_confirm(self):
		vntas_alb = {}
		for i in self:
			if i not in vntas_alb:
				vntas_alb[i]=i.picking_ids.ids
		t = super(sale_order, self).action_confirm()
		for i in self:
			if i in vntas_alb:
				for albaran_new in i.picking_ids:
					if albaran_new.id not in vntas_alb[i]:
						type_kardex = self.env["type.operation.kardex"].sudo().search(
          					[
                   				("code","like","%01%")
                       		],limit=1
               			).id
						albaran_new.type_operation_sunat_id = type_kardex
		return t
