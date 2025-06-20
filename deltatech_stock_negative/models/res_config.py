
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    no_negative_stock = fields.Boolean(
        string="No negative stock",
        help="Allows you to prohibit negative stock quantities.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    no_negative_stock = fields.Boolean(
        related="company_id.no_negative_stock",
        string="No negative stock",
        readonly=False,
        help="Allows you to prohibit negative stock quantities.",
    )
