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
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    # Copia los datos del archivo cargado al archivo temporal
                    tmp_file.write(record.fichero)
                    tmp_file.flush()
                    # Obtiene la ruta del archivo temporal
                    file_path = tmp_file.name
                    logger.info('MI RUTA:')
                    logger.info(file_path)

                    excel = lw(file_path)
                    logger.info('leo el archivo')
                    hojas = excel.active

                    # filas = hojas.rows
                    # next(filas)

                    filas_totales = []

                    for fila in hojas.iter_rows(values_only=True):
                        filas_totales.append(fila)
                    # for fila in filas:
                    #     datos = {'name': '', 'detailed_type': ''}
                    #     for titulo, celda in zip(datos.keys(), fila):
                    #         datos[titulo] = celda.value
                        
                    #     filas_totales.append(datos)

                    logger.info(filas_totales)
        

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