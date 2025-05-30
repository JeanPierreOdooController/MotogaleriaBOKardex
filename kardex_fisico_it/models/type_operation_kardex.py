from odoo import models, fields

class TypeOperationKardex(models.Model):
    _name="type.operation.kardex"
    
    name=fields.Char('Nombre')
    code=fields.Char('Codigo')