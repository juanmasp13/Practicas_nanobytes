from odoo import models, fields, api
import openpyxl
import logging
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento")
    nombre_fichero = fields.Char(string="Nombre del fichero")
    

