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

    mostrar_boton = fields.Boolean(string="mostrar boton", default=False)

    def _compute_mostrar_boton(self):
        for record in self:
            group_ids = self.env['res.users'].browse([self.env.user.id]).groups_id
            record.mostrar_boton = self._context.get('active_model') == 'sale.order' or group_ids in self.env.ref('account_financial_risk.group_overpass_partner_risk_exception').id