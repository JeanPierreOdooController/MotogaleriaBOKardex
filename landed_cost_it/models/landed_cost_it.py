# -*- coding: utf-8 -*-

from mimetypes import init
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import base64
from io import BytesIO
import subprocess
import sys

def install(package):
	subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
	import openpyxl
except:
	install('openpyxl==3.0.5')


##SE VUELVE A PONER EL CAMPO AQUI YA QUE SE NECESITA PARA CALCULO DE GV Y NO ES POSIBLE DEPENDER DEL CAMPO KARDEX_VALORADO_IT YA QUE ESTE DEPENDE DE GV
class stock_move(models.Model):
	_inherit = 'stock.move'

	price_unit_it = fields.Float('Precio Unitario',digits=(12,8))

class LandedCostIt(models.Model):
	_name = 'landed.cost.it'
	_inherit = ['mail.thread']

	name = fields.Char(string='Nombre')

	prorratear_en = fields.Selection([('cantidad', 'Por Cantidad'), ('valor', 'Por Valor')],string='Prorratear en funcion', required=True, default='cantidad')

	picking_ids = fields.Many2many('stock.picking', 'gastos_vinculado_picking_rel', 'gastos_id', 'picking_id', string='Albaranes')
	detalle_ids = fields.One2many('landed.cost.it.line', 'gastos_id', 'Detalle')
	company_id = fields.Many2one('res.company',string=u'Compañia',required=True, default=lambda self: self.env.company,readonly=True)
	invoice_ids = fields.One2many('landed.cost.invoice.line', 'landed_id',string='Facturas')
	purchase_ids = fields.One2many('landed.cost.purchase.line', 'landed_id',string='Ordenes de Compra')
	advalorem_ids = fields.One2many('landed.cost.advalorem.line', 'landed_id',string='Advalorem')
	
	state = fields.Selection([('draft', 'Borrador'), ('done', 'Finalizado')],string='Estado', default='draft')
	total_flete = fields.Float(string='Total GV', digits=(12, 2), store=True)
	total_flete_usd = fields.Float(string='Total GV USD', digits=(12, 2))
	total_factor = fields.Float(string='Total Factor', digits=(12, 2), store=True)
	date_kardex = fields.Datetime(string='Fecha Kardex')
	purchase_origin_id = fields.Many2one('purchase.order',string='Pedido de Compra')

	def get_info(self):
		
		picks = self.env['stock.picking'].search([('landed_cost_id','=',self.id)])
		
		if picks:
			for p in picks:
				self.picking_ids = [(6, 0, [p.id])]
		
		self.agregar_lineas()
		self.invoice_ids.unlink()
		self.purchase_ids.unlink()		
		purchases = self.env['purchase.order'].search([('landed_cost_id','=',self.id),('state','in',['purchase','done'])])
		for purchase in purchases:
			for line in purchase.order_line:
				if line.product_id.is_landed_cost:
					vals = {
						'purchase_id': line.id,
						'purchase_date': line.order_id.date_order.date(),
						'name': line.order_id.name,
						'partner_id': line.order_id.partner_id.id,
						'product_id': line.product_id.id,
						'price_total_signed': line.price_subtotal * line.tc_landed if line.order_id.currency_id.name != 'PEN' else line.price_subtotal,
						'tc': line.tc_landed,
						'currency_id': line.order_id.currency_id.id,
						'price_total': line.price_subtotal,
						'company_id': line.company_id.id,
					}
					self.write({'purchase_ids' :([(0,0,vals)]) })
					self._change_flete()
		
	def get_invoices(self):
		wizard = self.env['get.landed.invoices.wizard'].create({
			'landed_id': self.id,
			'company_id':self.company_id.id
		})
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_get_landed_invoices_wizard' % module)
		return {
			'name':u'Seleccionar Facturas',
			'res_id':wizard.id,
			'view_mode': 'form',
			'res_model': 'get.landed.invoices.wizard',
			'view_id': view.id,
			'context': self.env.context,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}

	def get_purchases(self):
		wizard = self.env['get.landed.purchases.wizard'].create({
			'landed_id': self.id,
			'company_id':self.company_id.id
		})
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_get_landed_purchases_wizard' % module)
		return {
			'name':u'Seleccionar Compras',
			'res_id':wizard.id,
			'view_mode': 'form',
			'res_model': 'get.landed.purchases.wizard',
			'view_id': view.id,
			'context': self.env.context,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}

	@api.onchange('invoice_ids','purchase_ids')
	def _change_flete(self):
		flete = 0
		flete_usd = 0
		usd = self.env.ref('base.USD')
		for elem in self.purchase_ids:
			if elem.currency_id.id == usd.id:
				flete += elem.price_total_signed
				flete_usd += elem.price_total
			else:
				flete += elem.price_total_signed
				from datetime import datetime, timedelta
				tc = self.env['res.currency.rate'].search([('currency_id','=',usd.id),('name','=',(elem.date_approve - timedelta(hours=5)).date() )],limit=1)
				flete_usd += elem.price_total_signed / (tc.sale_type or 1)
		for elem in self.invoice_ids:
			if elem.invoice_id.move_id.currency_id.id == usd.id:
				flete += elem.debit
				tc = self.env['res.currency.rate'].search([('currency_id','=',usd.id),('name','=',elem.invoice_date)],limit=1)
				flete_usd += (elem.amount_currency if elem.amount_currency !=0 else elem.debit/(tc.sale_type or 1))
			else:
				flete += elem.debit
				tc = self.env['res.currency.rate'].search([('currency_id','=',usd.id),('name','=',elem.invoice_date)],limit=1)
				flete_usd += elem.debit/(tc.sale_type or 1)

		self.total_flete = flete
		self.total_flete_usd = flete_usd

	@api.model
	def create(self, vals):
		id_seq = self.env['ir.sequence'].search([('name', '=', 'Gastos Vinculados IT'),('company_id','=',self.env.company.id)],limit=1)

		if not id_seq:
			id_seq = self.env['ir.sequence'].create({'name': 'Gastos Vinculados IT', 'company_id': self.env.company.id, 'implementation': 'no_gap','active': True, 'prefix': 'GV-', 'padding': 4, 'number_increment': 1, 'number_next_actual': 1})

		vals['name'] = id_seq._next()
		t = super(LandedCostIt, self).create(vals)
		return t

	def unlink(self):
		if self.state == 'done':
			raise UserError('No se puede eliminar un Gasto Vinculado Terminado')

		for i in self.picking_ids:
			i.unlink()

		for i in self.detalle_ids:
			i.unlink()

		t = super(LandedCostIt, self).unlink()
		return t

	def borrador(self):		
		self.write({'state': 'draft'})	

	def procesar(self):
		self.state = 'done'
	
	def calcular(self):
		self._change_flete()
		total_fle_lines = 0
		for i in self.detalle_ids:
			total_prorrateo = 0
			for m in self.detalle_ids:
				total_prorrateo += m.cantidad_rel if self.prorratear_en == 'cantidad' else m.valor_rel_signed

			i.factor = ((i.cantidad_rel if self.prorratear_en == 'cantidad' else i.valor_rel_signed) /
						total_prorrateo) if total_prorrateo != 0 else 0
			valor_mn = sum(line['valormn'] for line in self.advalorem_ids.filtered(lambda line: line.product_id.id == i.stock_move_id.product_id.id and line.picking_id.id == i.stock_move_id.picking_id.id))
			valor_me = sum(line['valorme'] for line in self.advalorem_ids.filtered(lambda line: line.product_id.id == i.stock_move_id.product_id.id and line.picking_id.id == i.stock_move_id.picking_id.id))
			i.flete = (i.factor * self.total_flete)
			i.flete_usd = (i.factor * self.total_flete_usd)
			i.advalorem = valor_mn or 0
			i.advalorem_usd = valor_me or 0
			i.total = i.flete + i.advalorem + i.valor_rel_signed
			i.total_usd = i.flete_usd + i.advalorem_usd + i.valor_rel
			total_fle_lines +=  i.flete
			
		#REDONDEO
		if len(self.detalle_ids)>0:
			diferencia_flete = 0
			if total_fle_lines < self.total_flete:
				diferencia_flete = self.total_flete - total_fle_lines
				self.detalle_ids[0].flete = self.detalle_ids[0].flete + diferencia_flete

			if total_fle_lines > self.total_flete:
				diferencia_flete = total_fle_lines - self.total_flete
				self.detalle_ids[0].flete = self.detalle_ids[0].flete - diferencia_flete

		return True

	def agregar_lineas(self):
		self.ensure_one()
		for i in self.detalle_ids:
			i.unlink()

		for i in self.picking_ids:
			for j in i.move_ids_without_package: 
				data = {
					'stock_move_id': j.id,
					'gastos_id': self.id,
				}
				self.env['landed.cost.it.line'].create(data)
		
class LandedCostItLine(models.Model):
	_name = 'landed.cost.it.line'
	stock_move_id = fields.Many2one('stock.move', 'Stock Move')
	gastos_id = fields.Many2one('landed.cost.it', 'Gastos Vinculado',ondelete="cascade")

	picking_rel = fields.Many2one('stock.picking',string='Referencia', related='stock_move_id.picking_id')
	origen_rel = fields.Many2one('stock.location', string='De',related='stock_move_id.location_id')
	destino_rel = fields.Many2one('stock.location',string='Para', related='stock_move_id.location_dest_id')
	producto_rel = fields.Many2one('product.product',string='Producto', related='stock_move_id.product_id')
	unidad_rel = fields.Many2one('uom.uom',string='Unidad de Medida', related='stock_move_id.product_uom')
	cantidad_rel = fields.Float(string='Cantidad', related='stock_move_id.product_qty')
	#precio_unitario_rel = fields.Float(string='Precio Unitario', related='stock_move_id.price_unit_it',store=True, digits=(64,8))
	precio_unitario_rel = fields.Float(string='Precio Unitario', compute="get_price_unit_signed",store=True, digits=(64,8))
	precio_unit_signed = fields.Float(string='Precio Unitario Soles', compute="get_price_unit_signed",store=True, digits=(64,8))
	valor_rel = fields.Float(string='Valor', compute="get_valor_rel",store=True)
	valor_rel_signed = fields.Float(string='Valor Soles', compute="get_valor_rel",store=True)
	
	valuation_id = fields.Many2one('stock.valuation.layer','Valoracion')

	factor = fields.Float(string='Factor', digits=(12, 10))
	flete = fields.Float(string='Total GV PEN', digits=(12, 6))
	flete_usd = fields.Float(string='Total GV USD', digits=(12, 6))
	advalorem = fields.Float(string='Advalorem PEN', digits=(12, 6))
	advalorem_usd = fields.Float(string='Advalorem USD', digits=(12, 6))
	total = fields.Float(string='Valor Total PEN', digits=(12, 6))
	total_usd = fields.Float(string='Valor Total USD', digits=(12, 6))

	@api.depends('stock_move_id.price_unit_it','stock_move_id.picking_id.tc','stock_move_id.picking_id.kardex_date','stock_move_id.picking_id.invoice_id')
	def get_price_unit_signed(self):
		for record in self:
			rate = record.stock_move_id.picking_id.tc or 1
		
			currency = self.env.ref('base.USD')
			tc = self.env['res.currency.rate'].search([('name','=',record.stock_move_id.picking_id.kardex_date.date()),('currency_id','=',currency.id)],limit=1)
			tcf = (tc.sale_type or 1)

			if (record.stock_move_id.purchase_line_id.order_id.currency_id.name or record.stock_move_id.company_id.currency_id.name) == 'PEN':
				record.precio_unitario_rel = (record.stock_move_id.price_unit_it or 0)/( rate if rate>0 else tcf)
				record.precio_unit_signed = (record.stock_move_id.price_unit_it or 0)
			elif (record.stock_move_id.purchase_line_id.order_id.currency_id.name or record.stock_move_id.company_id.currency_id.name) == 'USD':
				record.precio_unitario_rel = (record.stock_move_id.price_unit_it or 0)
				record.precio_unit_signed = (record.stock_move_id.price_unit_it or 0) * (rate if rate>0 else tcf)
			else:
				record.precio_unitario_rel = (record.stock_move_id.price_unit_it or 0) * (rate)  / tcf
				record.precio_unit_signed = (record.stock_move_id.price_unit_it or 0) * (rate)


	@api.depends('stock_move_id.product_qty','precio_unitario_rel','precio_unit_signed')
	def get_valor_rel(self):
		for record in self:
			record.valor_rel = record.stock_move_id.product_qty * record.precio_unitario_rel
			record.valor_rel_signed = record.stock_move_id.product_qty * record.precio_unit_signed

class LandedCostInvoiceLine(models.Model):
	_name = 'landed.cost.invoice.line'
	
	landed_id = fields.Many2one('landed.cost.it', 'Gastos Vinculado',ondelete="cascade")
	invoice_id = fields.Many2one('account.move.line',string='Factura')
	invoice_date = fields.Date(string='Fecha Factura')
	type_document_id = fields.Many2one('l10n_latam.document.type',string='Tipo de Documento')
	nro_comp = fields.Char(string='Nro Comprobante')
	date = fields.Date(string='Fecha Contable')
	partner_id = fields.Many2one('res.partner',string='Socio')
	product_id = fields.Many2one('product.product',string='Producto')
	debit = fields.Float(string='Debe',digits=(64,2))
	amount_currency = fields.Float(string='Monto Me',digits=(64,2))
	tc = fields.Float(string='TC',digits=(12,4))
	type_landed_cost_id = fields.Many2one('landed.cost.it.type',string='Tipo G.V.')
	company_id = fields.Many2one('res.company',string=u'Compañía')

class LandedCostPurchaseLine(models.Model):
	_name = 'landed.cost.purchase.line'
	
	landed_id = fields.Many2one('landed.cost.it', 'Gastos Vinculado',ondelete="cascade")
	purchase_id = fields.Many2one('purchase.order.line',string='Compra')
	purchase_date = fields.Date(string='Fecha Pedido')
	name = fields.Char(string='Pedido')
	partner_id = fields.Many2one('res.partner',string='Socio')
	product_id = fields.Many2one('product.product',string='Producto')
	price_total_signed = fields.Float(string='Total Soles',digits=(64,2))
	tc = fields.Float(string='TC',digits=(12,4))
	currency_id = fields.Many2one('res.currency',string='Moneda')
	price_total = fields.Float(string='Total',digits=(64,2))
	company_id = fields.Many2one('res.company',string=u'Compañía')

class LandedCostAdvaloremLine(models.Model):
	_name = 'landed.cost.advalorem.line'
	_description = 'Landed Cost Advalorem Line'

	productos_ids = fields.Many2many('product.product',compute="get_productos_ids")
	picking_ids = fields.Many2many('stock.picking',compute="get_picking_ids")

	landed_id = fields.Many2one('landed.cost.it', 'Gastos Vinculado')
	invoice_id = fields.Many2one('account.move.line',string='Factura')
	picking_id = fields.Many2one('stock.picking',string='Referencia')
	product_id = fields.Many2one('product.product',string='Producto')
	valormn = fields.Float(string='Valor MN',digits=(12,2))
	valorme = fields.Float(string='Valor ME',digits=(12,2))

	@api.depends('landed_id','picking_id')
	def get_productos_ids(self):
		for i in self:
			ids = []
			for l in self.landed_id.detalle_ids.filtered(lambda r: r.picking_rel.id == i.picking_id.id):
				if l.producto_rel.id not in ids:
					ids.append(l.producto_rel.id)
			i.productos_ids = ids


	@api.depends('landed_id')
	def get_picking_ids(self):
		for i in self:
			i.picking_ids = i.landed_id.picking_ids.ids

