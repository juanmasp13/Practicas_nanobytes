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
            logger.info(id.move_line_id.qty_done)
            logger.info(id.move_line_id.product_uom_qty)
        #return super(MrpProductionWorkcenterLine, self).do_finish()
            