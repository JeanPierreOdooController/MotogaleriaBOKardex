# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import *
from datetime import timedelta

class AccountConfigSettings(models.TransientModel):
	_inherit = "res.config.settings"
	origen_nro_compra = fields.Boolean(related="company_id.origen_nro_compra",string="Origen - Nro De Compra Llenado Automatico",readonly=False)
	etiqueta_lote = fields.Boolean(related="company_id.etiqueta_lote",string="Mostrar Lotes En Etiquetas De Factura",readonly=False)
	descript_move_l = fields.Boolean(related="company_id.descript_move_l",string="Mostrar Lotes En Descripción De Operaciones",readonly=False)
	fecha_caducidad = fields.Boolean(related="company_id.fecha_caducidad",string="Mostrar Fecha de Caducidad de los Lotes En Descripción De Operaciones",readonly=False)

class Company(models.Model):
	_inherit = "res.company"
	origen_nro_compra = fields.Boolean(string="Origen - Nro De Compra Llenado Automatico", default=True)
	etiqueta_lote = fields.Boolean(string="Mostrar Lotes En Etiquetas De Factura", default=True)
	descript_move_l = fields.Boolean(string="Mostrar Lotes En Descripción De Operaciones", default=True)
	fecha_caducidad = fields.Boolean(string="Mostrar Fecha de Caducidad de los Lotes En Descripción De Operaciones", default=True)

