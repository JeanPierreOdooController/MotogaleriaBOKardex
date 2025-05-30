import xlrd
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import base64
import os, os.path
import csv
from os import listdir
import sys

class Download_xls(http.Controller):
    
    @http.route('/web/binary/saldo_inicial_template', type='http', auth="public")
    def saldo_inicial_template(self, **kw):

        invoice_xls = request.env['ir.attachment'].sudo().search([('name','=','saldo_inicial_template.xlsx')])
        filecontent = invoice_xls.datas
        filename = 'Plantilla Saldo Inicial.xlsx'
        filecontent = base64.b64decode(filecontent)
            

        return request.make_response(filecontent,
            [('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', content_disposition(filename))])


















class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def download_template_iniical(self):
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/saldo_inicial_template',
            'target': 'new',
            }


    lotes_file = fields.Binary('Nro de Lotes',help="Archivo csv con el listado de series, separador requerido es |")
    errores_txt = fields.Text("Errores de Importación Lotes")
    tipo_import_lot = fields.Selection([
            ('name','Nombre Producto'),
            ('default_code','Codigo Interno Producto')
        ],
        u'Columna para Importación para Producto',
        default='default_code'
    )
    remove_rest = fields.Boolean(u'Remover líneas que no están en el archivo a importar', default=True)



    def get_read_lotes(self):
        import base64
        import xlrd

        if not self.lotes_file:
            raise UserError("Debe cargar un archivo de importación.")
        decoded_file = base64.b64decode(self.lotes_file)
        wb = xlrd.open_workbook(file_contents=decoded_file)
        sheet = wb.sheet_by_index(0)


        cont = 0
        verificacion_lotes = []
        contenedor_lotes = {}
        errores = ""
        # Evitar la cabecera 
        for row in range(1,sheet.nrows):
            data_linea = [sheet.cell(row,col).value for col in range(6)]
            
            if len(data_linea)==6:
                if data_linea[1]:
                    data_linea[1] = str(data_linea[1]).strip()
                    if data_linea[1][-2:] == '.0':
                        data_linea[1] = data_linea[1][:-2]

                data_linea[2] = float(data_linea[2])
                if (data_linea[0].strip(),str(data_linea[1]).strip()) in verificacion_lotes:
                    if ("El nro de lote esta duplicado: (" + data_linea[0].strip() +"," +str(data_linea[1]).strip() + ")\n")  in errores:
                        pass
                    else:
                        errores += ("El nro de lote esta duplicado: (" + data_linea[0].strip() +"," +str(data_linea[1]).strip() + ")\n")
                verificacion_lotes.append( (data_linea[0].strip(),str(data_linea[1]).strip()) )
    
                producto = self.env['product.product'].search([
                    (self.tipo_import_lot,'=',data_linea[0].strip())
                ])
                if not producto:
                    if ("No existe el producto: " + data_linea[0].strip() + "\n" ) in errores:
                        continue
                    else:
                        errores += "No existe el producto: " + data_linea[0].strip()  + "\n"
                        continue

                existe_lote = self.env['stock.lot'].search([
                    ('name','=',str(data_linea[1]).strip()),
                    ('product_id.'+self.tipo_import_lot,'=',data_linea[0].strip()),
                    ('location_id','=', self.location_dest_id.id)
                ])
                if len(existe_lote)>0:
                    errores += "Ya existe el lote para el producto seleccionado: (" + data_linea[0].strip()+ "," + str(data_linea[1]).strip() + ")\n"
                key_imp = None
                if producto[0].tracking == 'lot':
                    key_imp= (producto[0].id,str(data_linea[1]).strip())
                if producto[0].tracking == 'serial':
                    key_imp= (producto[0].id,'serie')
                if producto[0].tracking == 'none':
                    key_imp= (producto[0].id,'none')
                if key_imp==None:
                    errores += "El producto: " + data_linea[0].strip()  + "no tiene seguimiento por lotes o series\n"

                if key_imp in contenedor_lotes:
                    if producto[0].tracking == 'lot':
                        detalle_lotes = contenedor_lotes[key_imp]
                        detalle_lotes[0][2] += data_linea[2]
                        contenedor_lotes[key_imp] = detalle_lotes
                    else:
                        #if True:
                        detalle_lotes = contenedor_lotes[key_imp]
                        detalle_lotes.append(data_linea)
                        contenedor_lotes[key_imp] = detalle_lotes
                else:
                    contenedor_lotes[key_imp] = [data_linea]
        
        self.errores_txt = errores

        if errores !="":
            raise UserError(str(   errores    ))
#			return

        if self.state == 'draft':                    

            for elem in contenedor_lotes:
                #C310|0E0VHV|67|01/18/2020|78.76
                # raise UserError(f"{contenedor_lotes[elem][0][5]}")
                cuenta_analitica=self.env['account.analytic.account'].search([
                    ('name','=',contenedor_lotes[elem][0][5])
                ],limit=1)
#				etiqueta_analitica=self.env['account.analytic.tag'].search([
#					('name','=',contenedor_lotes[elem][0][6])
#				],limit=1)
    
                data = {
                    'product_id':elem[0],
                    'product_uom_qty':len(contenedor_lotes[elem]) if self.env['product.product'].browse(elem[0]).tracking == 'serial' else float(contenedor_lotes[elem][0][2]),
                    'name':self.env['product.product'].browse(elem[0]).name,
                    'product_uom':self.env['product.product'].browse(elem[0]).uom_id.id,
                    'location_id':self.location_id.id,
                    'location_dest_id':self.location_dest_id.id,
                    'picking_type_id':self.picking_type_id.id,
                    'price_unit_it':float(contenedor_lotes[elem][0][4]) if contenedor_lotes[elem][0][4] != "" else 0,
                    'analytic_account_id':cuenta_analitica.id if cuenta_analitica else None,
#					'analytic_tag_id':etiqueta_analitica.id if etiqueta_analitica else None
                }
    
                

                self.write({'move_ids_without_package':[(0,0,data)]})                    
            self.action_confirm()
            for lineas_eliminanr in self.move_line_ids_without_package:
                if lineas_eliminanr.tracking == 'serial':
                    lineas_eliminanr.unlink()
                elif lineas_eliminanr.tracking == 'lot':
                    lineas_eliminanr.unlink()
                elif lineas_eliminanr.tracking == 'none':
                    lineas_eliminanr.unlink()
            
            for i in self.move_ids_without_package:
                if i.product_id.tracking == 'serial':
                    data = {
                        'product_id':i.product_id.id,
                        'move_id':i.id,
                        'next_serial_count':i.product_uom_qty,
                        'next_serial_number':1,
                    }
                    obj_tmp = self.env['stock.assign.serial'].create(data)
                    obj_tmp.generate_serial_numbers()

            for elem in contenedor_lotes:
                #C310|0E0VHV|67|01/18/2020|78.76|
                if self.env['product.product'].browse(elem[0]).tracking == 'lot':
                    elem_move_picking = None
                    elem_move_pickingx = self.env['stock.move'].search([
                        ('picking_id','=',self.id),
                        ('product_id','=',elem[0]),
                        ('product_uom_qty','=',float(contenedor_lotes[elem][0][2]))
                    ])
                    for e in elem_move_pickingx:
                        conexion = self.env['stock.move.line'].search([('move_id','=',e.id)])
                        if len(conexion) == 0:
                            elem_move_picking = e
                            
                    if len(elem_move_picking)>1:
                        raise UserError("dos stockmoves:" +str(elem_move_picking.product_id.default_code))
                    move_line_vals = {
                        'picking_id': self.id,
                        'location_dest_id': self.location_dest_id.id,
                        'location_id': self.location_id.id,
                        'product_id': elem_move_picking.product_id.id,
                        'product_uom_id': elem_move_picking.product_uom.id,
                        'quantity': float(contenedor_lotes[elem][0][2]),
                        'quantity_product_uom': float(contenedor_lotes[elem][0][2]),
                        'package_level_id':False,
                        'move_id':elem_move_picking.id,
                    }
                    self.env['stock.move.line'].create(move_line_vals)
                elif self.env['product.product'].browse(elem[0]).tracking == 'none':
                    elem_move_picking = self.env['stock.move'].search([
                        ('picking_id','=',self.id),
                        ('product_id','=',elem[0])
                    ])
                    if len(elem_move_picking)>1:
                        raise UserError("dos stockmoves:" +str(elem_move_picking.product_id.default_code))
                    move_line_vals = {
                        'picking_id': self.id,
                        'location_dest_id': self.location_dest_id.id,
                        'location_id': self.location_id.id,
                        'product_id': elem_move_picking.product_id.id,
                        'product_uom_id': elem_move_picking.product_uom.id,
                        'quantity': float(contenedor_lotes[elem][0][2]),
                        'quantity_product_uom': float(contenedor_lotes[elem][0][2]),
                        'package_level_id':False,
                        'move_id':elem_move_picking.id,
                    }
                    self.env['stock.move.line'].create(move_line_vals)
        for i in self.move_line_ids_without_package:
            i.lot_name = False



        for elem in contenedor_lotes:
            producto_obj = self.env['product.product'].browse(elem[0])
            if producto_obj.tracking == 'serial':
                lineas_por_actualizar = self.move_line_ids_without_package.filtered(lambda r: r.product_id.id == elem[0])
                if len(lineas_por_actualizar) == 0:
                    raise UserError("No existe en el albaran el producto: " +  self.env['product.product'].browse(elem[0]).name)

                if len( lineas_por_actualizar ) >= len(contenedor_lotes[elem]) :
                    cont = 0
                    for actual_lot in contenedor_lotes[elem]:
                        lineas_por_actualizar[cont].lot_name = actual_lot[1]
                        lineas_por_actualizar[cont].quantity = 1
                        lineas_por_actualizar[cont].quantity_product_uom = 1
                        cont += 1
                else:
                    raise UserError("El nro de lotes es mayor para el producto: " +  lineas_por_actualizar[0].product_id.name)
            elif producto_obj.tracking == 'lot':					
                lineas_por_actualizar = self.move_line_ids_without_package.filtered(lambda r: r.product_id.id == elem[0] and not r.lot_name)
                if len(lineas_por_actualizar) == 0:
                    lineas_por_actualizar = self.move_line_ids_without_package.filtered(lambda r: r.product_id.id == elem[0] and r.move_id.product_uom_qty > r.move_id.quantity_done)
                    if len(lineas_por_actualizar) > 0:
                        lineas_por_actualizar = lineas_por_actualizar[0]
                        for x in range(len(contenedor_lotes[elem])):
                            lineas_por_actualizar = lineas_por_actualizar.copy()
                            lineas_por_actualizar.lot_name = False
                            lineas_por_actualizar.quantity = 0
                            lineas_por_actualizar.quantity_product_uom = 0
                    else:
                        raise UserError("No existe en el albaran el producto: " +  self.env['product.product'].browse(elem[0]).name)

                if len( lineas_por_actualizar ) >= len(contenedor_lotes[elem]) :
                    cont = 0
                    for actual_lot in contenedor_lotes[elem]:
                        lineas_por_actualizar[cont].lot_name = actual_lot[1]
                        lineas_por_actualizar[cont].quantity = contenedor_lotes[elem][0][2]
                        lineas_por_actualizar[cont].quantity_product_uom = contenedor_lotes[elem][0][2]
                        lineas_por_actualizar[cont].expiration_date = contenedor_lotes[elem][0][3]
                        cont += 1
                else:
                    raise UserError("El nro de lotes es mayor para el producto: " +  lineas_por_actualizar[0].product_id.name)

            elif producto_obj.tracking == 'none':						
                lineas_por_actualizar = self.move_line_ids_without_package.filtered(lambda r: r.product_id.id == elem[0] and not r.lot_name)
                if len(lineas_por_actualizar) == 0:
                    raise UserError("No existe en el albaran el producto: " +  self.env['product.product'].browse(elem[0]).name)
                if len( lineas_por_actualizar ) >= len(contenedor_lotes[elem]) :
                    cont = 0
                    for actual_lot in contenedor_lotes[elem]:
                        lineas_por_actualizar[cont].quantity = contenedor_lotes[elem][0][2]
                        lineas_por_actualizar[cont].quantity_product_uom = contenedor_lotes[elem][0][2]
                        cont += 1
                else:
                    raise UserError("El nro de lotes es mayor para el producto: " +  lineas_por_actualizar[0].product_id.name)
