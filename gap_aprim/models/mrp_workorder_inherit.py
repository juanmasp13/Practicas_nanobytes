from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import logging
logger = logging.getLogger(__name__)

class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.workorder"

    def do_finish(self):
        self.button_finish()
        return super(MrpProductionWorkcenterLine, self).do_finish()
    
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        logger.info("SACANDO CONTEXT")
        for workorder in self.workorder_ids:
            logger.info(workorder.component_id)
            