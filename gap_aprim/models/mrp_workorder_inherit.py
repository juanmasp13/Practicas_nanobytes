from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero
import logging
logger = logging.getLogger(__name__)

class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.workorder"

    def do_finish(self):
        for id in self.check_ids:
            qty_result = id.component_id.qty_available - id.qty_done
            logger.info("CANTIDAD ANTERIOR")
            logger.info(id.component_id.qty_available)
            logger.info("CANTIDAD A RESTAR")
            logger.info(id.qty_done)
            logger.info("NUEVA CANTIDAD")
            logger.info(qty_result)
            logger.info(id.move_id)
            logger.info("---------------")
            logger.info("product_uom_qty")
            logger.info(id.move_id.product_uom_qty)
            logger.info("product_qty_available")
            logger.info(id.move_id.product_uom_qty)
            logger.info("quantity_done")
            logger.info(id.move_id.quantity_done)
            logger.info("product_qty")
            logger.info(id.move_id.product_qty)
            logger.info("should_consume_qty")
            logger.info(id.move_id.should_consume_qty)
            logger.info("reserved_availability")
            logger.info(id.move_id.reserved_availability)
            logger.info("product_virtual_available")
            logger.info(id.move_id.product_virtual_available)
            logger.info("---------------")
        #return super(MrpProductionWorkcenterLine, self).do_finish()
            