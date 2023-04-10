# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
import logging
logger = logging.getLogger(__name__)

class PartnerRiskExceededWizInherit(models.TransientModel):
    _inherit = "partner.risk.exceeded.wiz"
    _description = "Partner Risk Exceeded Wizard"

    def button_continue(self):
        logger.info(self._context)