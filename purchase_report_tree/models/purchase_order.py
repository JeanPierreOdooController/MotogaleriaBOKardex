from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit="purchase.order"
    
    account_analytic_id=fields.Many2one(
        'account.analytic.account',
        string='Cuenta Analitica'
    )
    