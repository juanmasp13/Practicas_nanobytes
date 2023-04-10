from odoo import fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    
    def _compute_selection(self):
        selection = [()]
        if self.picking_type_code == 'outgoing':
            selection = [('aprobacion', 'Aprobación'), ('assigned',)]
        
        return selection

    state = fields.Selection(selection_add=_compute_selection()) 

    def button_validate(self):
        if self.move_line_ids.qty_done > self.move_line_ids.product_id.qty_available and self.picking_type_code == 'outgoing':
            raise UserError("La cantidad de salida (%s) es mayor que la cantidad de stock disponible (%s)" % (self.move_line_ids_without_package.qty_done,self.move_line_ids_without_package.product_id.qty_available))
        

        return super(StockPickingInherit, self).button_validate()
    
