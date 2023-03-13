from odoo import models, fields, api
from openpyxl import load_workbook as lw
import logging
import tempfile
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento")
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def mostrar_binario(self):
        logger.info(self.fichero)
        for record in self:
            if record.fichero:
                # Crea un archivo temporal
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    # Copia los datos del archivo cargado al archivo temporal
                    tmp_file.write(record.my_binary_field)
                    tmp_file.flush()

                    # Obtiene la ruta del archivo temporal
                    file_path = tmp_file.name
                    logger.info(file_path)
        

    # @api.multi
    # def get_file_path(self):
    #     for record in self:
    #         if record.fichero:
    #             # Crea un archivo temporal
    #             with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #                 # Copia los datos del archivo cargado al archivo temporal
    #                 tmp_file.write(record.my_binary_field)
    #                 tmp_file.flush()

    #                 # Obtiene la ruta del archivo temporal
    #                 file_path = tmp_file.name

    #                 # Retorna la ruta del archivo temporal
    #                 return file_path