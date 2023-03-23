from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from openpyxl import load_workbook as lw
import datetime
import base64
import xlrd
import logging, io
logger = logging.getLogger(__name__)

class ProductsProductsInheritance(models.Model):
    _inherit="product.product"

    descatalogado = fields.Boolean(default=False)

class importProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import Products Wizard'

    category_id = fields.Many2one('product.category', string="Categoría", required=True)
    fichero = fields.Binary(string="Documento", attachment=False, required=True)
    log_importacion = fields.Text(string="Productos no importados:", readonly=True)
    descatalogar = fields.Boolean(string="Descatalogar no encontrados") 
    
    def leer_excel_sin_cabecera(self):
        if self.fichero:
            opt = {}
            num_filas, filas = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
            filas.pop(0)
            #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
            return filas

    def registrar_templates(self):
        filas = self.leer_excel_sin_cabecera()
        num_fila = 1
        ids_no_descatalogados = []
        self.log_importacion = ''
        for fila in filas:
            campos = {3:'Nombre', 5:'Atributo 1', 6:'Atributo 2', 7:'Valores 1', 9:'Valores 2',}
            fallo = False
            for campo in campos:
                if fila[campo] == '':
                    log = "En la fila %s: el campo " + campos[campo] + " está vacío.\n" % str(num_fila)
                    self.log_importacion = (self.log_importacion or '') + log
                    fallo = True

            atributo1 = self.env['product.attribute'].search([('name', '=', fila[5])]) #Compruebo que existe el atributo 1
            if not atributo1:
                log = "En la fila %s: el atributo %s no existe.\n" % (str(num_fila), fila[5])
                self.log_importacion = (self.log_importacion or '') + log
                fallo = True

            atributo2 = self.env['product.attribute'].search([('name', '=', fila[6])]) #Compruebo que existe el atributo 2
            if not atributo2:
                log = "En la fila %s: el atributo %s no existe.\n" % (str(num_fila), fila[6])
                self.log_importacion = (self.log_importacion or '') + log
                fallo = True

            if fallo:
                num_fila += 1
                continue

                       
            valores_attr1 = self.env['product.attribute.value'].search([('attribute_id', '=', atributo1.id), ('name', '=', fila[7])]) #ID DE LOS VALORES DEL ATRIBUTO 1
            if not valores_attr1: #Si existen los valores del atributo 1 lo agregamos a la lista 
                log = "En la fila %s: para el atributo %s no existe el valor %s.\n" % (str(num_fila), atributo1.name, fila[7])
                if self.log_importacion:
                    self.log_importacion = self.log_importacion + log
                else:
                    self.log_importacion = log
                fallo = True

            if fallo:
                num_fila += 1
                continue

            valores_attr2 = self.env['product.attribute.value'].search([('attribute_id', '=', atributo2.id), ('name', '=', fila[9])]) #ID DE LOS VALORES DEL ATRIBUTO 2
            if not valores_attr2: #De la misma forma para los valores del atributo 2
                log = "En la fila %s: para el atributo %s no existe el valor %s.\n" % (str(num_fila), atributo2.name, fila[9])
                if self.log_importacion:
                    self.log_importacion = self.log_importacion + log
                else:
                    self.log_importacion = log                      
                fallo = True

            if fallo:
                num_fila += 1
                continue
            
            template = self.env['product.template'].search([('name', '=', fila[3])]) #BUSCAMOS TEMPLATE

            if template:
                logger.info('Para el template %s con el atributo %s y %s con el valor %s y %s' % (fila[3], fila[5], fila[6], fila[7], fila[9]))
                attribute_line1 = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', template.id), ('attribute_id', '=', atributo1.id)])
                if attribute_line1: #Si existe el attribute line cogemos los valores de los atributos que tenía y lo agregamos a la lista
                    if valores_attr1.id not in attribute_line1.value_ids.ids:
                        attribute_line1.write({'value_ids': [(4, valores_attr1.id)]}) #Añadimos los valores nuevos
                else: #Si no existe el attribute line lo creamos
                    attribute_line1 = self.env['product.template.attribute.line'].create({'attribute_id': atributo1.id, 'product_tmpl_id': template.id, 'value_ids': [valores_attr1.id,]})

                attribute_line2 = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', template.id), ('attribute_id', '=', atributo2.id)])
                if attribute_line2: #Si existe el attribute line cogemos los valores de los atributos que tenía y lo agregamos a la lista
                    if valores_attr2.id not in attribute_line2.value_ids.ids:
                        attribute_line2.write({'value_ids': [(4, valores_attr2.id)]}) #Añadimos los valores nuevos
                else: #Si no existe el attribute line lo creamos
                    attribute_line2 = self.env['product.template.attribute.line'].create({'attribute_id': atributo2.id, 'product_tmpl_id': template.id, 'value_ids': [valores_attr2.id,]})
                attribute_lines = [attribute_line1.id, attribute_line2.id]
            else: #Si no existe el template lo creamos directamente con sus líneas
                logger.info('CREANDO el template %s con el atributo %s y %s con el valor %s y %s' % (fila[3], fila[5], fila[6], fila[7], fila[9]))
                template = self.env['product.template'].create({'name': fila[3], 'categ_id': self.category_id.id, 'detailed_type': 'product'})
                attribute_lines = self.env['product.template.attribute.line'].create(
                    [{'attribute_id': atributo1.id, 'product_tmpl_id': template.id, 'value_ids': [valores_attr1.id,]},
                    {'attribute_id': atributo2.id, 'product_tmpl_id': template.id, 'value_ids': [valores_attr2.id,]}]
                    ).ids

            ids_combinacion = self.env['product.template.attribute.value'].search(
                [('product_tmpl_id', '=', template.id), ('attribute_line_id', 'in', attribute_lines), ('attribute_id', 'in', [atributo1.id, atributo2.id]), ('product_attribute_value_id', 'in', [valores_attr1.id, valores_attr2.id])]
                ).ids
            ids_combinacion = sorted(ids_combinacion)
            ids_combinacion =  ', '.join(str(num) for num in ids_combinacion)
            logger.info('IDS COMBINACION %s ' % ids_combinacion)
            logger.info('IDS A AGREGAR A LA LISTA DE NO DESCATALOGADOS: %s' % self.env['product.product'].search([('combination_indices', '=', ids_combinacion)]).id)
            ids_no_descatalogados.append(self.env['product.product'].search([('combination_indices', '=', ids_combinacion)]).id)
            num_fila += 1        

        if self.descatalogar: #Si la casilla de descatalogar está marcada le asignamos a todos los productos con esa categoría que están descatalogados
            productos_a_descatalogar = self.env['product.product'].search([('categ_id', '=', self.category_id.id),('id','not in',ids_no_descatalogados)])            #for producto in productos:
            productos_a_descatalogar.write({'descatalogado': True})
        
        return filas

    def registrar_productos(self):
        filas = self.registrar_templates()
        # campos requeridos en product.template: categ_id, detailed_type, name, product_variant_id, tracking, uom_id, uom_po_id
        for fila in filas:
            id_atributo1 = self.env['product.attribute'].search([('name', '=', fila[5])]).id                           
            id_atributo2 = self.env['product.attribute'].search([('name', '=', fila[6])]).id
            id_valor_atr_1 = self.env['product.attribute.value'].search([('attribute_id', '=', id_atributo1), ('name', '=', fila[7])]).id                         
            id_valor_atr_2 = self.env['product.attribute.value'].search([('attribute_id', '=', id_atributo2), ('name', '=', fila[9])]).id
            if id_valor_atr_1 and id_valor_atr_2:
                template_id = self.env['product.template'].search([('name', '=', fila[3])]).id
                ptav1 = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', template_id), ('attribute_id', '=', id_atributo1), ('product_attribute_value_id', '=', id_valor_atr_1)]).id
                ptav2 = self.env['product.template.attribute.value'].search([('product_tmpl_id', '=', template_id), ('attribute_id', '=', id_atributo2), ('product_attribute_value_id', '=', id_valor_atr_2)]).id
                combinacion = self.concatenar_combinacion(ptav1, ptav2)
                producto = self.env['product.product'].search([('combination_indices', '=', combinacion)])
                divisa_id = self.env['ir.model.data'].search([('model', '=', 'res.currency'), ('module', '=', 'base'), ('name', '=', fila[13])]).res_id
                if fila[0]:
                    external_id = self.env['ir.model.data'].search([('name', '=', fila[0])])               
                    if external_id:
                        producto = self.env['product.product'].browse([external_id.res_id])                     
                    else:
                        external_id = self.env['ir.model.data'].create({'name': fila[0], 'module': 'stock', 'model': 'product.product', 'res_id': producto.id})
                if fila[14]:
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 1')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[14]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[14]})
                if fila[15]:
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 2')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[15]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[15]})
                if fila[16]:
                    pricelist_id = self.env['product.pricelist'].search([('name', '=', 'PVP 3')]).id
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id), ('product_id', '=', producto.id)])
                    if pricelist_item:
                        pricelist_item.write({'fixed_price': fila[16]})
                    else:
                        pricelist_item = self.env['product.pricelist.item'].create({'pricelist_id': pricelist_id, 'product_id': producto.id, 'fixed_price': fila[16]})
                if fila[17]:
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
                
