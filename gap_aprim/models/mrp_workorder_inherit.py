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
            logger.info("Component id:")
            logger.info(id.component_id)
            logger.info("QTY DONE:")
            logger.info(id.qty_done)
            logger.info("QTY LINE:")
            logger.info(id.qty_line)