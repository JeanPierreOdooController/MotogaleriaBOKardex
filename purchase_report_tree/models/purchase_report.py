from odoo import models, api, fields
from odoo.exceptions import UserError

class PurchaseReport(models.Model):
    _inherit="purchase.report"
    account_analytic_id = fields.Many2one(
        'account.analytic.account', 
        string='Cuenta Analitica'
    )
    
    def _select(self):
        res=super()._select()
        res+=", po.account_analytic_id AS account_analytic_id"
        return res
    
    def _from(self):
        res=super()._from()
        res+=" LEFT JOIN account_analytic_account aa ON aa.id = po.account_analytic_id"
        return res
    
    def _group_by(self):
        res=super()._from()
        res+=", po.account_analytic_id"
        return res