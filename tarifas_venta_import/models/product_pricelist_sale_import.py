from odoo import models, fields, _
from odoo.exceptions import UserError
import tempfile
import binascii
import xlrd
import base64

class ProductPricelistSaleImport(models.TransientModel):
	_name = "product.pricelist.sale.import"
	_description = "Importador Tarifas Venta"

	file = fields.Binary(string='Archivo')
	tarifa_id = fields.Many2one('product.pricelist',string="Tarifa")
	import_tarifa_type = fields.Selection(
     	[
			('create','Crear Tarifas'),
			('update','Actualizar Tarifas')
    	],
      	string='Tipo de Operacion',
        required=True,
        default="create"
    )
 
	def download_template(self):
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/binary/download_tarifa_sale_import_template',
			'target': 'new',
		}	

	def tarifa_import(self):              
		fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
		try :
			fp.write(binascii.a2b_base64(self.file))
			fp.seek(0)
			values = {}
			workbook = xlrd.open_workbook(fp.name)
		except Exception:
			raise UserError(_("Sube un archivo .xlsx!")) 
		if not self.tarifa_id:
			raise UserError('Debe Escoger Una Tarifa')
		sheet = workbook.sheet_by_index(0)  
		for row_no in range(sheet.nrows):
			# Evitar las cabeceras
			if row_no <= 0:
				continue
			# Get xlsx line
			line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))   
			if line[0].strip()=='':
				raise UserError('El campo REFERENCIA INTERNA no puede estar vacío.')
			if line[1].strip() == '':
				raise UserError('El campo PRECIO FIJO no puede estar vacío')
			ref_interna=line[0].strip()
			precio_fijo=line[1].strip()
			# En caso se deba CREAR una tarifa
			if self.import_tarifa_type == 'create':
				values.update({
        			'sku':ref_interna,
					'fixed_price':precio_fijo,
				})
				res = self.product_create(values)
				continue
			# En caso se deba ACTUALIZAR una tarifa
			producto = self.env['product.product'].sudo().search(
       			[
              		('default_code', '=', ref_interna),
                	'|',
                 	('company_id', '=', self.env.company.id),
                  	('company_id', '=', False)
                ]
          	)
			if not producto:
				raise UserError(f'Producto no Encontrado: {ref_interna}')
			if len(producto)>1:
				raise UserError(f"Dos Productos con La Misma Referencia Interna: {ref_interna}")
			linea_tarifa = self.env['product.pricelist.item'].sudo().search(
       			[
              		('company_id', '=', self.tarifa_id.company_id.id),
                	('product_id', '=', producto.id),
                 	('pricelist_id', '=', self.tarifa_id.id),
                  	('applied_on', '=', '0_product_variant')
                ]
        	)
			if len(linea_tarifa)>1:
				raise UserError('Dos Tarifas Con El Mismo Producto Encontradas: ' + str(producto.default_code))
			if len(linea_tarifa)<=0:									
				raise UserError('Tarifas Para El Producto No Encontrada: ' + str(producto.default_code))
			precio_fijo = precio_fijo.replace("'","")
			linea_tarifa.sudo().write({'fixed_price':float(precio_fijo)})
		return self.env['popup.it'].get_message('SE IMPORTARON LAS TARIFAS DE MANERA CORRECTA.')
	
	def product_create(self, values):
		linea_tarifa = self.env['product.pricelist.item']
		sku=values.get('sku').strip()
		fixed_price= values.get('fixed_price').strip()
		producto = self.env['product.product'].sudo().search(
      		[
            	('default_code', '=', sku),
             	'|', 
              	('company_id', '=', self.env.company.id),
               	('company_id', '=', False)
            ])
		if len(producto)>1:
			raise UserError(f"Dos Productos con La Misma Referencia Interna: {sku}")
		if len(producto)<=0:
			raise UserError(f'Producto no Encontrado: {sku}')
		fixed_price = fixed_price.replace("'","")
		tarifa_repetida = self.env['product.pricelist.item'].sudo().search(
      		[
            	('pricelist_id', '=', self.tarifa_id.id), 
             	('company_id', '=', self.tarifa_id.company_id.id),
              	('applied_on', '=', '0_product_variant'),
               	('product_id', '=', producto.id)
            ])
		if not tarifa_repetida:
			vals = {
				'pricelist_id': self.tarifa_id.id,
				'applied_on': '0_product_variant',      
				'product_id': producto.id,
				'company_id': self.tarifa_id.company_id.id,
				'compute_price': 'fixed',
				'currency_id': self.tarifa_id.currency_id.id,
				'fixed_price': float(fixed_price)
			}
			return linea_tarifa.create(vals)
		if len(tarifa_repetida)>1:
			raise UserError('Dos Tarifas Encontradas Para El Producto: ' + str(producto.name))
		tarifa_repetida.sudo().write({'fixed_price':float(fixed_price)})  

	def verify_if_exists_product(self):
		fp = tempfile.NamedTemporaryFile(delete= False, suffix=".xlsx")
		try :
			fp.write(binascii.a2b_base64(self.file))
			fp.seek(0)
			workbook = xlrd.open_workbook(fp.name)
		except Exception:
			raise UserError(_("Sube un archivo .xlsx!"))

		duplicados = []
		sheet = workbook.sheet_by_index(0)
		# Buscar duplicados en el excel
		for row_no in range(sheet.nrows):
			# Evitar la cabecera
			if row_no <= 0:
				continue
			line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
   
			ref_interna = self.verify_product({'default_code': line[0]})
			duplicados.append(ref_interna) if ref_interna else None
		if not duplicados:
			return self.env['popup.it'].get_message('NO EXISTEN PRODUCTOS DUPLICADOS.')
		# Crear excel con los productos duplicados
		from xlsxwriter.workbook import Workbook
		import importlib
		import sys
		importlib.reload(sys)

		raise UserError(f"duplicados {duplicados}")
		ReportBase = self.env['report.base']
		direccion = self.env['main.parameter'].search(
      		[
            	('company_id','=',self.env.company.id)
            ],limit=1
        ).dir_create_file
		if not direccion:
			raise UserError(u'No existe un Directorio Exportadores configurado en Parametros Principales de Contabilidad para su Compañía')
		nombre_archivo='Productos_Existentes.xlsx'
		workbook = Workbook(direccion+nombre_archivo)
		workbook, formats = ReportBase.get_formats(workbook)
		worksheet = workbook.add_worksheet("Productos")
		worksheet.set_tab_color('blue')
  
		HEADERS = ['REFERENCIA INTERNA']
		worksheet = ReportBase.get_headers(worksheet,HEADERS,0,0,formats['boldbord'])
		row=1
		for line in duplicados:
			worksheet.write(row,0,line[0] if line[0] else '',formats['especial1'])				
			row += 1
		widths = [100,19]
		worksheet = ReportBase.resize_cells(worksheet,widths)
		workbook.close()
		f = open(direccion+nombre_archivo, 'rb')
		return self.env['popup.it'].get_file('Productos Duplicados.xlsx',base64.encodestring(b''.join(f.readlines())))
		
			

	def verify_product(self, values):
		s = str(values.get('default_code')).strip()
		default_code = s.rstrip('0').rstrip('.') if '.' in s else s
		product_id = self.env['product.template'].search(
      		[
            	('default_code','=', default_code)
            ],limit=1
    	)
		if product_id:
			return default_code
