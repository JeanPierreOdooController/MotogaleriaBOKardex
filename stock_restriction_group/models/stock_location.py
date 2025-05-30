# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class stock_location(models.Model):
    _inherit = 'stock.location'
    
    def unlink(self):
        if not self.env.user.has_group("stock_restriction_group.stock_location_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Ubicaciones'.")
        return super(stock_location,self).unlink()
    
    @api.model
    def create(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_location_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Ubicaciones'.")
        return super(stock_location,self).create(vals)
           
    def write(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_location_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Ubicaciones'.")
        return super(stock_location,self).write(vals)