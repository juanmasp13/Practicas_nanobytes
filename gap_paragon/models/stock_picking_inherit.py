from odoo import fields, models
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    
    def _compute_selection(self):
        # logger.info("PASO %s " % self.picking_type_code)
        # logger.info("%s " % self.picking_type_id)
        # logger.info("SOY %s " % self)
        logger.info(self._context)
        # logger.info(self.env.context.get('params')['id'])
        # id = self.env.context.get('params')['id']
        # registro = self.env['stock.picking'].browse(id).picking_type_code
        # logger.info(registro)
        if self.picking_type_code == 'outgoing':
            selection = [
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),
            ('aprobacion', 'Aprobación'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ]
        else:
            selection = [
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ]
        
        return selection
    

    state = fields.Selection(selection='_compute_selection', string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Aprobación: Un administrador debe validar el albarán.\n"
             " * Cancelled: The transfer has been cancelled.") 

    def button_validate(self):
        if self.move_line_ids.qty_done > self.move_line_ids.product_id.qty_available and self.picking_type_code == 'outgoing':
            raise UserError("La cantidad de salida (%s) es mayor que la cantidad de stock disponible (%s)" % (self.move_line_ids_without_package.qty_done,self.move_line_ids_without_package.product_id.qty_available))
        

        return super(StockPickingInherit, self).button_validate()
    
