from odoo import fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    #CANTIDAD DISPONIBLE: self.move_line_ids_without_package.product_id.qty_available 

    def button_validate(self):        
        raise UserError(self.move_line_ids_without_package.qty_available)
        super(StockPickingInherit, self).button_validate()