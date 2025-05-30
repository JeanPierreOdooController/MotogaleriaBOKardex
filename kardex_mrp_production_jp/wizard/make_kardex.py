# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from odoo.exceptions import UserError

class stock_move_line(models.Model):
	_inherit = 'stock.move.line'

	price_unit_it = fields.Float('Precio Unitario')

class mrp_production(models.Model):
	_inherit = 'mrp.production'

	def calcular_costos(self):
		for i in self:
			total = 0
			for linex in i.move_raw_ids:
				total += linex.quantity * linex.price_unit_it

			for linet in i.finished_move_line_ids:
				linet.move_id.price_unit_it = total / linet.move_id.quantity
				self.env.cr.execute("""
					update stock_move set price_unit_it = """+str(total / linet.move_id.quantity)+""" where id = """+str(linet.move_id.id)+"""
    				""")
				#linet.price_unit_it = total / linet.quantity if linet.quantity != 0 else 0

	def calcular_costos_dolar(self):
		for i in self:
			total = 0
			for linex in i.move_raw_ids:
				total += linex.quantity * linex.price_unit_it_dolar

			for linet in i.finished_move_line_ids:
				linet.move_id.price_unit_it_dolar = total / linet.move_id.quantity
				self.env.cr.execute("""
					update stock_move set price_unit_it_dolar = """+str(total / linet.move_id.quantity)+""" where id = """+str(linet.move_id.id)+"""
    				""")
				#linet.price_unit_it_dolar = total / linet.quantity if linet.quantity != 0 else 0
