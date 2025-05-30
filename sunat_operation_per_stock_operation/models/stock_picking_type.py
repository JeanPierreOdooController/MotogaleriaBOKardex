from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _inherit="stock.picking.type"
    
    default_sunat_operation = fields.Many2one('type.operation.kardex', string='Operacion Sunat por Defecto')