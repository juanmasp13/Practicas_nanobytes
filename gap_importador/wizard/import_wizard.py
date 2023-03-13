from odoo import models, fields, api
from openpyxl import load_workbook as lw
from odf import opendocument
from odf.table import Table, TableRow, TableCell
from odf.text import P
import logging, io
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento")
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def mostrar_binario(self):
        for record in self:
            if record.fichero:
                # logger.info('FICHERO BINARIO DESPUES DE USAR IOBYTES')
                # doc = ODSReader(file=io.BytesIO(record.fichero or b''))
                # contenido = doc._read_ods
                # logger.info(contenido)
                logger.info('FICHERO BINARIO CON RECORD.FICHERO')
                logger.info(record.fichero)
                logger.info('FICHERO BINARIO CON SELF.FICHERO')
                logger.info(self.fichero)
                

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

    def readSheet(self, sheet):
        name = sheet.getAttribute("name")
        rows = sheet.getElementsByType(TableRow)
        arrRows = []

        # for each row
        for row in rows:
            arrCells = []
            cells = row.getElementsByType(TableCell)

            # for each cell
            for count, cell in enumerate(cells, start=1):
                # repeated value?
                repeat = 0
                if count != len(cells):
                    repeat = cell.getAttribute("numbercolumnsrepeated")
                if not repeat:
                    repeat = 1
                    spanned = int(cell.getAttribute('numbercolumnsspanned') or 0)
                    # clone spanned cells
                    if self.clonespannedcolumns is not None and spanned > 1:
                        repeat = spanned

                ps = cell.getElementsByType(P)
                textContent = u""

                # for each text/text:span node
                for p in ps:
                    for n in p.childNodes:
                        if n.nodeType == 1 and n.tagName == "text:span":
                            for c in n.childNodes:
                                if c.nodeType == 3:
                                    textContent = u'{}{}'.format(textContent, n.data)

                        if n.nodeType == 3:
                            textContent = u'{}{}'.format(textContent, n.data)

                if textContent:
                    if not textContent.startswith("#"):  # ignore comments cells
                        for rr in range(int(repeat)):  # repeated?
                            arrCells.append(textContent)
                else:
                    for rr in range(int(repeat)):
                        arrCells.append("")

            # if row contained something
            if arrCells:
                arrRows.append(arrCells)

            #else:
            #    print ("Empty or commented row (", row_comment, ")")

        self.SHEETS[name] = arrRows

    def getSheet(self, name):
        return self.SHEETS[name]

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