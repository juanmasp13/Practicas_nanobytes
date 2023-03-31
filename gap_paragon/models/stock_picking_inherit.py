from odoo import fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):        
        raise UserError(self.move_line_ids_without_package)
        super(StockPickingInherit, self).button_validate()