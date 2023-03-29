from odoo import fields, models
import logging, io
logger = logging.getLogger(__name__)

class stockMoveInherit(models.Model):
    _inherit = "stock.move"

    fichero = fields.Binary(string="Subir report")

    def registrar_num_serie(self):
        logger.info("Hola")
