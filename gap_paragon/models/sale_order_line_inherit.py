from odoo import fields, models

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order"

    product_id = fields.Many2one('product.product', string="Producto")
    virtual_available = fields.Float(string="Inventario pronosticado", related="product_id.virtual_available")