from odoo import models, fields, api
from openpyxl import load_workbook as lw
import logging
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento")
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def mostrar_binario(self):
        logger.info(self.fichero)

    # def import_products(self):
    #     excel = lw(self.ruta_fichero)
    #     hojas = excel.active
    #     filas = hojas.rows
    #     next(filas)
    #     filas_totales = []
    #     for fila in filas:
    #         datos = {'name': '', 'detailed_type': ''}
    #         for titulo, celda in zip(datos.keys(), fila):
    #             datos[titulo] = celda.value
    #         filas_totales.append(datos)
    #     return self.env['product.template'].create(filas_totales)
    
    # def ruta_fichero(self):
    #     file_path = self.fichero.gettempdir()+'/productos.xlsx'
    #     return file_path
