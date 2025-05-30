

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    allow_negative_stock = fields.Boolean(string="Allow Negative Stock")
