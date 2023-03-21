from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from openpyxl import load_workbook as lw
import datetime
import base64
import xlrd
import logging, io
logger = logging.getLogger(__name__)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría", required=True)
    fichero = fields.Binary(string="Documento", attachment=False, required=True)
    log_importacion = fields.Text(string="Log Importacion", readonly=True) 


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
    
    def leer_excel_sin_cabecera(self):
        if self.fichero:
            opt = {}
            num_filas, filas = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
            filas.pop(0)
            #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
            return filas

    def registrar_templates(self):
        filas = self.leer_excel_sin_cabecera()
        registro = self.env['import.products.wizard'].search([('id', '=', self.id)])
        for fila in filas:
            atributo1 = self.env['product.attribute'].search([('name', '=', fila[5])]) #Compruebo que existe el atributo 1
            atributo2 = self.env['product.attribute'].search([('name', '=', fila[6])]) #Compruebo que existe el atributo 2
            if atributo1: #Si existe el atributo 1 y el atributo 2 hacemos el proceso
                if atributo2:
                    template = self.env['product.template'].search([('name', '=', fila[3])]) #BUSCAMOS TEMPLATE
                    lista_id1 = [] #Creamos una lista a la que le vamos a concatenar los valores del atributo 1
                    lista_id2 = [] #Creamos una lista a la que le vamos a concatenar los valores del atributo 2
                    valores_attr1 = self.env['product.attribute.value'].search([('attribute_id', '=', atributo1.id), ('name', '=', fila[7])]) #ID DE LOS VALORES DE LOS ATRIBUTOS
                    valores_attr2 = self.env['product.attribute.value'].search([('attribute_id', '=', atributo2.id), ('name', '=', fila[9])]) #ID DE LOS VALORES DE LOS ATRIBUTOS
                    if valores_attr1: #Si existen los valores de los atributos 
                        lista_id1.append(valores_attr1.id) #Si está bien escrito lo agregamos a la lista
                    else:                       
                        log = "Para el atributo %s no existe el valor %s" % (atributo1.name, fila[7])
                        registro.write({'log_importacion': registro.log_importacion + '\n' + log})
                    if valores_attr2:
                        lista_id2.append(valores_attr2.id)
                    else:
                        log = "Para el atributo %s no existe el valor %s" % (atributo2.name, fila[9])
                        registro.write({'log_importacion': registro.log_importacion + '\n' + log})                      
                    if valores_attr1 and valores_attr2: #Si existe el template buscamos si existe algun attribute line
                        if template:
                            logger.info("EXISTE EL TEMPLATE %s" % template.name)
                            attribute_line1 = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', template.id), ('attribute_id', '=', atributo1.id)])
                            attribute_line2 = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', template.id), ('attribute_id', '=', atributo2.id)])
                            if attribute_line1: #Si existe el attribute line cogemos los valores de los atributos que tenía y lo agregamos a la lista
                                attribute_line_vals_ids = attribute_line1.value_ids.ids
                                lista_id1 = list(dict.fromkeys(lista_id1+attribute_line_vals_ids)) #Elimino los valores de los atributos repetidos en la concatenación de los valores de los atributos
                                attribute_line1.write({'value_ids': [(6, 0, lista_id1)]}) #Añadimos los valores nuevos
                            else: #Si no existe el attribute line lo creamos
                                self.env['product.template.attribute.line'].create({'attribute_id': atributo1.id, 'product_tmpl_id': template.id, 'value_ids': lista_id1})
                            if attribute_line2: #Si existe el attribute line cogemos los valores de los atributos que tenía y lo agregamos a la lista
                                attribute_line_vals_ids = attribute_line2.value_ids.ids
                                lista_id2 = list(dict.fromkeys(lista_id2+attribute_line_vals_ids)) #Elimino los valores de los atributos repetidos en la concatenación de los valores de los atributos
                                attribute_line2.write({'value_ids': [(6, 0, lista_id2)]}) #Añadimos los valores nuevos
                            else: #Si no existe el attribute line lo creamos
                                self.env['product.template.attribute.line'].create({'attribute_id': atributo2.id, 'product_tmpl_id': template.id, 'value_ids': lista_id2})
                        else: #Si no existe el template lo creamos directamente con sus líneas
                            logger.info("El template %s no existe, lo creamos directamente" % fila[3])
                            product_template = self.env['product.template'].create({'name': fila[3], 'categ_id': self.category_id.id, 'detailed_type': 'product'})
                            attribute_line1 = self.env['product.template.attribute.line'].create({'attribute_id': atributo1.id, 'product_tmpl_id': product_template.id, 'value_ids': lista_id1})
                            attribute_line2 = self.env['product.template.attribute.line'].create({'attribute_id': atributo2.id, 'product_tmpl_id': product_template.id, 'value_ids': lista_id2})
                else:
                    log = "El atributo %s no existe" % fila[6]
                    registro.write({'log_importacion': registro.log_importacion + '\n' + log})
            else:
                log = "El atributo %s no existe" % fila[5]
                registro.write({'log_importacion': registro.log_importacion + '\n' + log}) 

                
        return filas

    def registrar_productos(self):
        filas = self.registrar_templates()
        # campos requeridos en product.template: categ_id, detailed_type, name, product_variant_id, tracking, uom_id, uom_po_id
        for fila in filas:
            template_id = self.env['product.template'].search([('name', '=', fila[3])]).id
            id_atributo1 = self.env['product.attribute'].search([('name', '=', fila[5])]).id                           
            id_atributo2 = self.env['product.attribute'].search([('name', '=', fila[6])]).id
            id_valor_atr_1 = self.env['product.attribute.value'].search([('attribute_id', '=', id_atributo1), ('name', '=', fila[7])]).id                         
            id_valor_atr_2 = self.env['product.attribute.value'].search([('attribute_id', '=', id_atributo2), ('name', '=', fila[9])]).id
            if id_valor_atr_1 and id_valor_atr_2:
                ptav1 = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', template_id), ('attribute_id', '=', id_atributo1), ('product_attribute_value_id', '=', id_valor_atr_1)]).id
                ptav2 = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', template_id), ('attribute_id', '=', id_atributo2), ('product_attribute_value_id', '=', id_valor_atr_2)]).id
                combinacion = self.concatenar_combinacion(ptav1, ptav2)
                producto = self.env['product.product'].search([('combination_indices', '=', combinacion)])
                logger.info('PARA EL PRODUCTO %s' % producto.display_name)
                divisa_id = self.env['ir.model.data'].search([('model', '=', 'res.currency'), ('module', '=', 'base'), ('name', '=', fila[13])]).res_id
                if fila[0] != '':
                    external_id = self.env['ir.model.data'].search([('name', '=', fila[0])])               
                    if external_id:
                        producto = self.env['product.product'].browse([external_id.res_id])                     
                    else:
                        external_id = self.env['ir.model.data'].create({'name': fila[0], 'module': 'stock', 'model': 'product.product', 'res_id': producto.id})
                if fila[14] != '':
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 1')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[14]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[14]})
                if fila[15] != '':
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 2')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[15]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[15]})
                if fila[16] != '':
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 3')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[16]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[16]})
                if fila[17] != '':
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP Final')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[17]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[17]})
                producto.write({'barcode': fila[1], 'default_code': fila[2], 'description': fila[11], 'standard_price': fila[12], 'currency_id': divisa_id})
        return {
        'context': self.env.context,
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'import.products.wizard',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    } 

                
                
    
    
    def concatenar_combinacion(self, num1, num2):
        if num1 > num2:
            return str(num2) + ',' + str(num1)
        else:
            return str(num1) + ',' + str(num2)               
                
                
    
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
                
