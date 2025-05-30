# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import tools
from datetime import datetime
from datetime import timedelta
import json
import base64

class kardex_master(models.Model):
	_name = 'kardex.master'
	_rec_name = 'company_id'


	company_id = fields.Many2one('res.company','Compañia',default=lambda self: self.env.company)
	widget_char = fields.Binary(compute='_compute_kardex_info',exportable=False)
	numero = fields.Integer('Entero',default=5)
	company_name = fields.Char(related='company_id.name')


	def update_date(self):
		self.numero = self.numero +1


	def action_analisis_kardex(self):
		exis = self.env['kardex.master'].search([('company_id','=',self.env.company.id)])
		if len(exis)>0:
			exis= exis[0]
		else:
			exis = self.env['kardex.master'].create({'company_id':self.env.company.id})

		return {
			'name': _('Kardex Análisis'),
			'res_model': 'kardex.master',
			'view_mode': 'form',
			'type': 'ir.actions.act_window',
			'res_id': exis.id,
		}

	def _compute_kardex_info(self):
		self.widget_char = {
			'company_id': self.company_id.name,
			'numero': self.numero,
		}