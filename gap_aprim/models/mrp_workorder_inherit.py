from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero
import logging
logger = logging.getLogger(__name__)

class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.workorder"

    def do_finish(self):
        logger.info(self.check_ids.component_id)
        logger.info(self.finished_product_check_ids)