# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EinvoiceCatalog25(models.Model):
	_name = 'einvoice.catalog.25'

	name = fields.Char(string='Nombre')
	code = fields.Char(string='Codigo',size=8)
	_order = 'code'