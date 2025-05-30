# -*- encoding: utf-8 -*-
from odoo import models

class PurchaseOrder(models.Model):
	_inherit='purchase.order'

	def button_confirm(self):
		vntas_alb = {}
		for i in self:
			if i not in vntas_alb:
				vntas_alb[i]=i.picking_ids.ids
		t = super(PurchaseOrder, self).button_confirm()
		for i in self:
			if i in vntas_alb:
				for albaran_new in i.picking_ids:
					if albaran_new.id not in vntas_alb[i]:
						type_kardex = self.env["type.operation.kardex"].sudo().search(
          					[
                   				("code","like","%02%")
                       		],limit=1
               			).id
						albaran_new.type_operation_sunat_id = type_kardex
		return t