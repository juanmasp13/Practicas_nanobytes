from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import logging
logger = logging.getLogger(__name__)

class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.workorder"

    def do_finish(self):
        res = super(MrpProductionWorkcenterLine, self).do_finish()
        for id in self.check_ids:
            if id.component_id and id.component_id.type == 'product':
                id.move_id._action_done()
        return res
    
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    #EMPEZAR CON EL STOCK.MOVE, PROBAR ACTION CANCEL, Y VER SI ME DEVUELVE STOCK Y UTILIZAR EL MÉTODO _GENERATE_BACKORDER

