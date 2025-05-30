from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit="stock.picking"
    
    @api.onchange('picking_type_id','state')
    def _onchange_picking_type_id(self):
        for rec in self:
            if rec.type_operation_sunat_id:
                return
            rec.type_operation_sunat_id=rec.picking_type_id.default_sunat_operation.id

        
