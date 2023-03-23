from odoo import fields, models

class stockProductLotInherit(models.Model):
    _inherit = "stock.production.lot"

    pallet_no = fields.Float(string='Pallet no.', digits=(0, 3))
    pmax = fields.Float(string='Pmax', digits=(0, 3))
    ff = fields.Float(string='FF', digits=(0, 3))
    voc = fields.Float(string='Voc', digits=(0, 3))
    isc = fields.Float(string='Isc', digits=(0, 3))
    vpm = fields.Float(string='Vpm', digits=(0, 3))
    ipm = fields.Float(string='Ipm', digits=(0, 3))