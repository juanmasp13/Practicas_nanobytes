from odoo import models, fields, api
from openpyxl import load_workbook as lw
from odf import opendocument
from odf.table import Table
import logging, io
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento")
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def mostrar_binario(self):
        logger.info('FICHERO BINARIO DEL FIELDS.BINARY')
        logger.info(self.fichero)
        for record in self:
            if record.fichero:
                logger.info('FICHERO BINARIO DESPUES DE USAR IOBYTES')
                doc = ODSReader(file=io.BytesIO(self.fichero or b''))
                logger.info(doc._read_ods)
                
                excel = lw(doc)
                logger.info('leo el archivo')
                hojas = excel.active

                filas = hojas.rows
                next(filas)

                filas_totales = []

                for fila in filas:
                    datos = {'name': '', 'detailed_type': ''}
                    for titulo, celda in zip(datos.keys(), fila):
                        datos[titulo] = celda.value
                    
                    filas_totales.append(datos)

                logger.info(filas_totales)

class ODSReader(object):
    # loads the file
    def __init__(self, file=None, content=None, clonespannedcolumns=None):
        if not content:
            self.clonespannedcolumns = clonespannedcolumns
            self.doc = opendocument.load(file)
        else:
            self.clonespannedcolumns = clonespannedcolumns
            self.doc = content
        self.SHEETS = {}
        for sheet in self.doc.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)

    def _read_ods(self, options):
            doc = ODSReader(file=io.BytesIO(self.fichero or b''))
            sheets = options['sheets'] = list(doc.SHEETS.keys())
            sheet = options['sheet'] = options.get('sheet') or sheets[0]

            content = [
                row
                for row in doc.getSheet(sheet)
                if any(x for x in row if x.strip())
            ]

            # return the file length as first value
            return content