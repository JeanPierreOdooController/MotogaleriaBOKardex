# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    def unlink(self):
        if not self.env.user.has_group("stock_restriction_group.stock_warehouse_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Almacén'.")
        return super(StockWarehouse,self).unlink()

    @api.model
    def create(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_warehouse_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Almacén'.")
        return super(StockWarehouse,self).create(vals)
           
    def write(self,vals):
        if not self.env.user.has_group("stock_restriction_group.stock_warehouse_restriction_group"):
            raise UserError("No Posee El Permiso: 'Permite Modificar Almacén'.")
        return super(StockWarehouse,self).write(vals)
        


        
