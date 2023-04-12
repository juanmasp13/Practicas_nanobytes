from odoo import fields, models, api
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    
    def _compute_selection(self):
        selection = selection = [
                    ('draft', 'Draft'),
                    ('waiting', 'Waiting Another Operation'),
                    ('confirmed', 'Waiting'),
                    ('assigned', 'Ready'),
                    ('done', 'Done'),
                    ('cancel', 'Cancelled'),
                ]
        params = self._context.get('params')
        if params:
            id_picking = params.get('id')
            if id_picking:
                tipo_mov = self.env['stock.picking'].browse(id_picking).picking_type_code
                if tipo_mov == 'outgoing':
                    selection = [
                    ('draft', 'Draft'),
                    ('waiting', 'Waiting Another Operation'),
                    ('confirmed', 'Waiting'),
                    ('assigned', 'Ready'),
                    ('aprobacion', 'Aprobación'),
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

    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'aprobacion'):
                picking.show_validate = False
            else:
                picking.show_validate = True

    def button_validate(self):
        if self.picking_type_code == 'outgoing':
            qty = 0
            logger.info("MOSTRANDO LOS MOVE LINES")
            logger.info(self.move_line_ids)
            for id in self.move_line_ids:
                qty += 1
            if qty > id.product_id.qty_available:
                raise UserError("La cantidad de salida (%s) es mayor que la cantidad de stock disponible (%s)" % (self.move_line_ids_without_package.qty_done,self.move_line_ids_without_package.product_id.qty_available))
        

        return super(StockPickingInherit, self).button_validate()
    
