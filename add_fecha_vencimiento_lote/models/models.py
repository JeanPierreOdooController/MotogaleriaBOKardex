from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	def add_fecha_vencimiento(self):
		import base64
		import xlrd

		if not self.lotes_file:
			raise UserError("Debe cargar un archivo de importación.")
		decoded_file = base64.b64decode(self.lotes_file)
		wb = xlrd.open_workbook(file_contents=decoded_file)
		sheet = wb.sheet_by_index(0)

		msg =""
		cont = 0
		verificacion_lotes = []
		contenedor_lotes = {}
		errores = ""
		# Evitar la cabecera 
		for row in range(1,sheet.nrows):
			data_linea = [sheet.cell(row,col).value for col in range(6)]
			
			if len(data_linea)==6:
				if data_linea[3] != '' and data_linea[3] != False:
					producto = self.env['product.product'].search([(self.tipo_import_lot,'=',data_linea[0].strip())])
					if len(producto)>0:
						if len(producto)>1:
							if ("Producto No Subido Las Fechas De Vencimiento, Porque Existen Dos Productos Iguales: " + str(data_linea[0].strip())) in msg:
								pass
							else:
								msg += "Producto No Subido Las Fechas De Vencimiento, Porque Existen Dos Productos Iguales: " + str(data_linea[0].strip()) + "\n"
						else:
							if producto.tracking in ('serial','lot'):
								lot_obj = self.env['stock.lot'].sudo().search([('name','=',data_linea[1].strip()),('product_id','=',producto.id,)])
								if len(lot_obj)>0:
									if len(lot_obj)>1:
										if ("Dos Lotes Encontrados Al Subir Las Fechas De Vencimiento: " + str(data_linea[1].strip()) + " Del Producto: "+str(data_linea[0].strip())) in msg:
											pass
										else:
											msg += "Dos Lotes Encontrados Al Subir Las Fechas De Vencimiento: " + str(data_linea[1].strip()) + " Del Producto: "+str(data_linea[0].strip()) + "\n"
									else:
										producto.use_expiration_date = True
										lot_obj.expiration_date = data_linea[3].strip() + " 05:00:00"
										lot_obj.removal_date = data_linea[3].strip() + " 05:00:00"
										lot_obj.use_date = data_linea[3].strip() + " 05:00:00"
										lot_obj.alert_date = data_linea[3].strip() + " 05:00:00"
								else:
									if ("Lote No Encontrado Al Subir Las Fechas De Vencimiento: " + str(data_linea[1].strip()) + " Del Producto: "+str(data_linea[0].strip())) in msg:
										pass
									else:
										msg += "Lote No Encontrado Al Subir Las Fechas De Vencimiento: " + str(data_linea[1].strip()) + " Del Producto: "+str(data_linea[0].strip()) + "\n"
							else:
								if ("Producto No Subido Fechas De Vencimiento, No Es Producto Que TRABAJE Con Lotes O Series Unicas: " + str(data_linea[0].strip())) in msg:
									pass
								else:
									msg += "Producto No Subido Fechas De Vencimiento, No Es Producto Que TRABAJE Con Lotes O Series Unicas: " + str(data_linea[0].strip()) + "\n"
					else:
						if ("Producto No Encontrado Al Subir Las Fechas De Vencimiento: " + str(data_linea[0].strip())) in msg:
							pass
						else:
							msg += "Producto No Encontrado Al Subir Las Fechas De Vencimiento: " + str(data_linea[0].strip()) + "\n"
		for s_move in self.move_ids_without_package:
			for s_move_line in s_move.move_line_ids:
				if s_move_line.lot_id.expiration_date:
					s_move_line.expiration_date = s_move_line.lot_id.expiration_date 
		if msg != "":
			self.errores_txt = "ERRORES FECHA VENCIMIENTO: "+ "\n" + msg + "\n"+"ERRORES DE IMPORTACION: "+ "\n" + (picking.errores_txt if picking.errores_txt else '')




