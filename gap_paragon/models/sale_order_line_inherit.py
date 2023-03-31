from odoo import fields, models

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    product_packaging_qty = fields.Integer('Packaging Quantity')
    virtual_available = fields.Float(string="Inventario pronosticado", related="product_id.virtual_available")

class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order"

    product_packaging_qty = fields.Integer('Packaging Quantity')
