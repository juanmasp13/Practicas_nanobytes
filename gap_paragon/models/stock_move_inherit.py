from odoo import fields, models
import logging, io
logger = logging.getLogger(__name__)

class stockMoveInherit(models.Model):
    _inherit = "stock.move"

    fichero = fields.Binary(string="Subir report")

    def registrar_num_serie(self):
        logger.info("Hola")

class PartnerRiskExceededWizInherit(models.TransientModel):
    _inherit = "partner.risk.exceeded.wiz"

    def mostrar_context(self):
        logger.info(self._context.get('active_model'))
