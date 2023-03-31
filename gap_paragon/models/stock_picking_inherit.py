from odoo import fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    #CANTIDAD DISPONIBLE: self.move_line_ids_without_package.product_id.qty_available 
    #CANTIDAD EXPORTACION: self.move_line_ids_without_package.qty_done

    def button_validate(self):
        if self.move_line_ids_without_package.qty_done > self.move_line_ids_without_package.product_id.qty_available:
            raise UserError("La cantidad de salida (%s) es mayor que la cantidad de stock disponible (%s)" % (self.move_line_ids_without_package.qty_done,self.move_line_ids_without_package.product_id.qty_available))
        super(StockPickingInherit, self).button_validate()