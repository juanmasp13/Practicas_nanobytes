from odoo import fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):        
        super(StockPickingInherit, self).button_validate()
        raise UserError(self.move_line_ids_without_package)