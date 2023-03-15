from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from openpyxl import load_workbook as lw
import datetime
import base64
import xlrd
from xlrd import xlsx
import logging, io
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría")
    fichero = fields.Binary(string="Documento", attachment=False)
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def registrar_productos(self):
        for record in self:
            if record.fichero:
                logger.info('FICHERO BINARIO')
                opt = {}
                num_filas, valores = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
                valores.pop(0)
                #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
                # campos requeridos en product.template: categ_id, detailed_type, name, product_variant_id, tracking, uom_id, uom_po_id
                
                registros = []

                for valor in valores:
                    logger.info('VALOR 3')
                    logger.info(valor[3])
                    logger.info('LONGITUD VALOR 3')
                    logger.info(len(valor[3]))
                    if self.env['product.template'].search([('name', '=', valor[3])], limit=1):
                        template = self.env['product.template'].search([('name', '=', valor[3])])
                        template_id = template.id
                        if template:
                            #logger.info('ID ATRIBUTO:')
                            #logger.info(atr.attribute_id)
                            atributo = self.env['product.attribute'].search([('name', '=', valor[5])])
                            logger.info('Nombre atributo:')
                            logger.info(atributo)
                            #logger.info(valor[5])
                            #logger.info(atributo.id)
                            if (atributo.name == valor[5]):
                                valor_atr = self.env['product.attribute.value'].search([('attribute_id', '=', atributo.id)])
                                for valor_atributo in valor_atr:
                                    #logger.info('VALOR ATRIBUTO: ')
                                    #logger.info(valor_atributo.name)
                                    if (valor_atributo.name == valor[7]):
                                        logger.info('Para %s:' % valor[5])
                                        logger.info('Valores de atributo 1 bien %s' % valor[7])
                                        logger.info('Buscando los ids de los valores del atributo')
                                        values_ids = self.env['product.attribute.value'].search([('attribute_id', '=', atributo.id)])
                                        logger.info('CREANDO ATTRIBUTE LINE')
                                        attribute_line = self.env['product.template.attribute.line'].create({'attribute_id': atributo.id, 'product_tmpl_id': template_id, 'value_ids': values_ids.ids})
                                        logger.info(attribute_line)
                                        logger.info('CREANDO PRODUCT')
                                        attribute_line_ids = [attribute_line.id]
                                        producto = self.env['product.product'].create({'name': valor[3], 'product_tmpl_id': template_id, 'categ_id': record.category_id.id, 'attribute_line_ids': attribute_line_ids, 'detailed_type': 'product'})
                                        logger.info(producto)
                                    else:
                                        logger.info('Valores de atributo 1 mal %s' % valor[7])
                            elif(atributo.name == valor[6]):
                                valor_atr = self.env['product.attribute.value'].search([('attribute_id', '=', atributo.id)])
                                for valor_atributo in valor_atr:
                                    #logger.info('VALOR ATRIBUTO: ')
                                    #logger.info(valor_atributo.name)
                                    if (valor_atributo.name == valor[8]):
                                        #logger.info('Para %s:' % valor[6])
                                        #logger.info('Valores de atributo 1 bien %s' % valor[8])
                                        logger.info('Valores de atributo 1 bien %s' % valor[8])
                                    else:
                                        logger.info('Valores de atributo 1 mal %s' % valor[8])
                    else:
                        logger.info('No existe el template: %s' % valor[3])
                        
                    # vals['name'] = valor[0]
                    # vals['detailed_type'] = valor[1]
                    # registros.append(vals)
                #template = self.env['product.template'].create(registros)
                
                
    
    def _read_xls(self, options):
        book = xlrd.open_workbook(file_contents=base64.b64decode(self.fichero) or b'') # IMPORTANTE EL base64.b64decode, es necesario hacerselo al campo para poder leerlo
        sheets = options['sheets'] = book.sheet_names()
        sheet = options['sheet'] = options.get('sheet') or sheets[0]
        return self._read_xls_book(book, sheet)

    def _read_xls_book(self, book, sheet_name):
        sheet = book.sheet_by_name(sheet_name)
        rows = []
        # emulate Sheet.get_rows for pre-0.9.4
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                            'row': rowx,
                            'col': colx,
                            'cell_value': xlrd.error_text_from_code.get(cell.value, _("unknown error code %s", cell.value))
                        }
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                rows.append(values)

        # return the file length as first value
        return sheet.nrows, rows
                
