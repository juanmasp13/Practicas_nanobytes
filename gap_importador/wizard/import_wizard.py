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

    category_id = fields.Many2one('product.category', string="Categoría", required=True)
    fichero = fields.Binary(string="Documento", attachment=False)
    nombre_fichero = fields.Char(string="Nombre del fichero")


    def old_registrar_productos(self):
        for record in self:
            if record.fichero:
                opt = {}
                num_filas, valores = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
                valores.pop(0)
                #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
                # campos requeridos en product.template: categ_id, detailed_type, name, product_variant_id, tracking, uom_id, uom_po_id

                for valor in valores:
                    logger.info('TEMPLATE: ')
                    logger.info(valor[3])
                    if self.env['product.template'].search([('name', '=', valor[3])], limit=1):
                        template = self.env['product.template'].search([('name', '=', valor[3])])
                        if template:
                            atributo = self.env['product.attribute'].search([('name', '=', valor[5])])
                            if (atributo.name == valor[5]):
                                ids_valores_attr = self.env['product.attribute.value'].search([('attribute_id', '=', atributo.id)])
                                logger.info('CREANDO ATTRIBUTE LINE')
                                attribute_line = self.env['product.template.attribute.line'].create({'attribute_id': atributo.id, 'product_tmpl_id': template.id, 'value_ids': ids_valores_attr.ids})
                                for valor_atributo in ids_valores_attr:
                                    if (valor_atributo.name == valor[7]):
                                        logger.info('CREANDO PRODUCT CON ATRIBUTO')
                                        logger.info(atributo.name)
                                        logger.info('CON VALOR')
                                        logger.info(valor_atributo.name)
                                        attribute_line_ids = [attribute_line.id]
                                        producto = self.env['product.product'].create({'name': valor[3], 'product_tmpl_id': template.id, 'categ_id': record.category_id.id, 'attribute_line_ids': attribute_line_ids, 'detailed_type': 'product'})
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
    
    def registrar_productos(self):
        for record in self:
            if record.fichero:
                opt = {}
                num_filas, filas = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
                filas.pop(0)
                #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
                # campos requeridos en product.template: categ_id, detailed_type, name, product_variant_id, tracking, uom_id, uom_po_id
                for fila in filas:
                    logger.info('ESTAMOS EN LA FILA DE: %s' % fila[3])
                    template = self.env['product.template'].search([('name', '=', fila[3])]) #BUSCAMOS TEMPLATE
                    atributos = self.env['product.attribute'].search(['|', ('name', '=', fila[5]), ('name', '=', fila[6])]) #BUSCAMOS ATRIBUTOS
                    logger.info('IDS ATRIBUTOS: %s' % atributos.ids)
                    if atributos:
                        lista_id = []
                        for atributo in atributos:
                            logger.info('Para el atributo: %s' % atributo.name)
                            logger.info('COLUMNA 5: %s' % fila[5])
                            logger.info('COLUMNA 6: %s' % fila[6])
                            if (atributo.name == fila[5]) or (atributo.name == fila[6]):
                                ids_valores_attr = self.env['product.attribute.value'].search([('attribute_id', '=', atributo.id)]) #ID DE LOS VALORES DE LOS ATRIBUTOS
                                logger.info('IDS VALORES ATRIBUTOS: %s' % ids_valores_attr)
                                if ids_valores_attr:
                                    if (atributo.name == fila[5]):
                                        logger.info('ESTAMOS EN EL PRIMER IF')
                                        for id in ids_valores_attr:
                                            logger.info('Tenemos el valor: %s' % id.name) 
                                            if id.name == fila[7]:
                                                logger.info('Valores de atributo 1 bien, añadiendo a la lista')
                                                lista_id.append(id.id)
                                    elif (atributo.name == fila[6]):
                                        logger.info('ESTAMOS EN EL SEGUNDO IF')
                                        for id in ids_valores_attr:
                                            logger.info('Tenemos el valor: %s' % id.name)
                                            logger.info('Y EN EL EXCEL TENEMOS EL VALOR: %s' % fila[8]) 
                                            if id.name == fila[8]:
                                                logger.info('Valores de atributo 2 bien, añadiendo a la lista')
                                                lista_id.append(id.id)
                                if template:
                                    attribute_line = self.env['product.template.attribute.line'].create({'attribute_id': atributo.id, 'product_tmpl_id': template.id, 'value_ids': lista_id})
                                else:
                                    producto = self.env['product.template'].create({'name': fila[3], 'categ_id': record.category_id.id, 'detailed_type': 'product'})
                                    attribute_line = self.env['product.template.attribute.line'].create({'attribute_id': atributo.id, 'product_tmpl_id': producto.id, 'value_ids': lista_id})
                
                
    
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
                
