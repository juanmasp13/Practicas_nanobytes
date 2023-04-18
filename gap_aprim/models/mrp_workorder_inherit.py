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
            new_qty = id.component_id.write({'qty_available': qty_result})
            logger.info("NUEVA CANTIDAD")
            logger.info(qty_result)
            logger.info("EL WRITE")
            logger.info(new_qty)
            logger.info(id.move_id)
            logger.info(id.move_line_id)
            if not new_qty:
                raise UserError("No se ha podido actualizar la cantidad de %s" % id.component_id.name)
        #return super(MrpProductionWorkcenterLine, self).do_finish()
            