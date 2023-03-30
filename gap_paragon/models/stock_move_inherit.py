from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging, io
import base64
import datetime
import xlrd
logger = logging.getLogger(__name__)

class stockMoveInherit(models.Model):
    _inherit = "stock.move"

    fichero = fields.Binary(string="Subir report")

    def registrar_num_serie(self):       
        logger.info(self.product_qty)
        num_serie = []
        filas = self.leer_excel_sin_cabecera()
        cont = 0
        for fila in filas:
            qty = int(self.product_qty)
            if cont <= qty:
                vals = {
                    'name': fila[0],'product_id': self.product_id.id, 'company_id': self._context.get('default_company_id'),
                    'pallet_no': fila[1], 'pmax': fila[5], 'ff': fila[8], 'voc': fila[3], 'isc': fila[4], 'vpm': fila[6], 'ipm': fila[7],
                    }
                num_serie.append(vals)
            else:
                break
            cont += 1
        ids_num_serie = self.env['stock.production.lot'].create(num_serie)
        stock_move_line = self.env['stock_move_line'].search(
            [('picking_id', '=', self._context.get('default_picking_id')), ('move_id', '=', self.id), ('product_id', '=', self.product_id.id)]
            )
        for id in ids_num_serie.ids:
            stock_move_line.write({'lot_id': id})
        return {
        'context': self.env['partner.risk.exceeded.wiz'].browse([self._context.get('params')[id]]).context,
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'partner.risk.exceeded.wiz',
        'res_id': self._context.get('params')[id],
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
        }

    def leer_excel_sin_cabecera(self):
        if self.fichero:
            opt = {}
            num_filas, filas = self._read_xls(options=opt) #En valores guardo una lista con listas de valores
            filas.pop(0)
            #Aquí estan todos los valores excluyendo la cabecera gracias al método pop()
            return filas
        else:
            raise UserError("¡ERROR! Debes seleccionar un fichero excel para realizar la importación.")

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
    

class PartnerRiskExceededWizInherit(models.TransientModel):
    _inherit = "partner.risk.exceeded.wiz"

    mostrar_boton = fields.Boolean(string="mostrar boton", compute="_compute_mostrar_boton")

    def _compute_mostrar_boton(self):
        for record in self:
            group_ids = self.env['res.users'].browse([self.env.user.id]).groups_id
            record.mostrar_boton = self._context.get('active_model') == 'sale.order' or group_ids in self.env.ref('account_financial_risk.group_overpass_partner_risk_exception').id