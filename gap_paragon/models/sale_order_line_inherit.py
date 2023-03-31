from odoo import fields, models

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order"

    virtual_available = fields.Float(string="Inventario pronosticado", related="product_id.virtual_available")