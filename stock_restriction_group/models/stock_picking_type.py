# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class stock_picking_type(models.Model):
    _inherit = 'stock.picking.type'
    
    def unlink(self):
        if not self.env.user.has_group("stock_restriction_group.stock_picking_type_restriction_group"):   
            raise UserError("No Posee El Permiso: 'Permite Modificar El Tipo de Operación'.")
        return super(stock_picking_type,self).unlink()
            
    @api.model
    def create(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_picking_type_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar El Tipo de Operación'.")
        return super(stock_picking_type,self).create(vals)
            
    def write(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_picking_type_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar El Tipo de Operación'.")
        return super(stock_picking_type,self).write(vals)
            
