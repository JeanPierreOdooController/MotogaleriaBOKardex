# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from contextlib import ExitStack, contextmanager
class res_company(models.Model):
	_inherit = 'res.company'

	check_nro_guia_obligatorio = fields.Boolean('Nro Guia Obligatorio',default=True)

class res_config_settings(models.TransientModel):
	_inherit = 'res.config.settings'

	check_nro_guia_obligatorio = fields.Boolean('Nro Guia Obligatorio',related="company_id.check_nro_guia_obligatorio",readonly=False)

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	invoice_id = fields.Many2one("account.move",string="Factura",copy=False)


class account_move(models.Model):
	_inherit = 'account.move'

	picking_ids = fields.Many2many('stock.picking', 'stock_picking_move_id_rel', 'picking_id', 'move_id', string='Albaranes',copy=False)

	@api.model
	def create(self,vals):
		t = super(account_move,self).create(vals)
		if t.picking_ids.ids:
			for i in t.picking_ids:
				i.invoice_id = t.id
		return t




	def new_modify(self):
		if self.picking_ids:
			new_invoice = self
			productos= {}
			if self.picking_ids:
				for line_picking in self.picking_ids.mapped('move_ids_without_package'):
					if line_picking.state == 'done':
						if line_picking.product_id.id in productos:
							productos[line_picking.product_id.id] = productos[line_picking.product_id.id] + line_picking.quantity
						else:
							productos[line_picking.product_id.id] = line_picking.quantity

				idsnew = []
				for line_invoice in new_invoice.line_ids:
					if line_invoice.product_id.id and line_invoice.product_id.type != 'service':
						if line_invoice.product_id.id in productos and line_invoice.quantity >= productos[line_invoice.product_id.id]:
							line_invoice.quantity = productos[line_invoice.product_id.id]
							idsnew.append(line_invoice.id)
						elif line_invoice.product_id.id in productos:
							productos[line_invoice.product_id.id] =  productos[line_invoice.product_id.id]-line_invoice.quantity
							idsnew.append(line_invoice.id)
						else:
							line_invoice.unlink()

					#line_invoice._onchange_mark_recompute_taxes()
					#_recompute_cash_rounding_lines ese pareciera ser no revisa a fondo ya que calculaba bien

				for i in self.picking_ids:
					i.invoice_id = self.id


class purchaseadvancepaymentinv(models.TransientModel):
	_name = 'purchase.advance.payment.inv'
	_description = "purchase advance payment inv"

	picking_ids = fields.Many2many('stock.picking', 'stock_picking_purchase_advance_payment_inv', 'picking_id', 'purchase_advance_id', string='Albaranes')
	picking_ids_compute = fields.Many2many('stock.picking',compute="get_picking_ids_compute")

	@api.depends('picking_ids')
	def get_picking_ids_compute(self):
		purchase = self.env['purchase.order'].browse(self._context.get('active_id', False))
		self.picking_ids_compute = purchase.picking_ids.filtered(lambda r: r.state == 'done' and r.invoice_id.id == False ).ids

	def create_invoices(self):
		purchase = self.env['purchase.order'].browse(self._context.get('active_id', False))
		t = purchase.with_context({'picking_ids':self.picking_ids.ids,'wizard_complete':True,'create_bill':True}).action_view_invoice(invoices = self.env['account.move'].browse(self.env.context['invoices']))
		return t

class purchase_order(models.Model):
	_inherit ='purchase.order'


	def action_view_invoice_it(self):
		if len(self.invoice_ids)==0:
			raise UserError("No tiene Facturas de Proveedor Registradas")
		return {
				'name': 'Facturas de Proveedor',
				'view_mode': 'tree,form',
				'res_model': 'account.move',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain':[('id','in',self.invoice_ids.ids)],
				'context': {
					'active_id': self.id,
				}
		}


	def action_view_invoice(self, invoices=False):
		if 'wizard_complete' in self.env.context:
			pass
		else:
			return {
					'name': 'Pedido de Compra',
					'view_mode': 'form',
					'res_model': 'purchase.advance.payment.inv',
					'view_id': False,
					'type': 'ir.actions.act_window',
					'target': 'new',
					'context': {
						'active_id': self[0].id,
						'active_ids': self.ids,
						'invoices': invoices.ids,
					}
			}
		t = super(purchase_order,self).action_view_invoice(invoices)
		if invoices:
			for i in invoices:
				i.picking_ids = self.env.context['picking_ids']
				i.new_modify()
		return t



class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = 'sale.advance.payment.inv'

	picking_ids = fields.Many2many('stock.picking', 'stock_picking_sale_advance_payment_inv', 'picking_id', 'sale_advance_id', string='Albaranes')
	picking_ids_compute = fields.Many2many('stock.picking',compute="get_picking_ids_compute")

	
	@api.depends('picking_ids')
	def get_picking_ids_compute(self):
		sale = self.env['sale.order'].browse(self._context.get('active_id', False))
		self.picking_ids_compute = sale.picking_ids.filtered(lambda r: r.state == 'done' and r.invoice_id.id == False ).ids


	def create_invoices(self):
		Sale = self.env['sale.order'].browse(self._context.get('active_id', False))
		before_invoices = Sale.invoice_ids
		res = super(SaleAdvancePaymentInv, self).create_invoices()
		after_invoices = Sale.invoice_ids
		new_invoice = after_invoices - before_invoices
		if len(new_invoice) == 1:
			self.picking_ids.write({'invoice_id': new_invoice.id})
			ebill = self.env['ir.module.module'].search([('name', '=', 'ebill')])
			if ebill and ebill.state == 'installed':
				for picking in self.picking_ids:						
					if self.env.company.check_nro_guia_obligatorio and not picking.numberg:
						raise UserError("El albaran no cuenta con Nro. de Guia y esta configurado como obligatorio.")
					if picking.numberg:
						self.env['move.guide.line'].create({
								'move_id': new_invoice.id,
								'numberg': picking.numberg
							})
			l10n_pe_transportref=self.env['ir.module.module'].search([('name','=','l10n_pe_edi_pse_factura')])
			if l10n_pe_transportref and l10n_pe_transportref.state=='installed':
				for picking in self.picking_ids:						
					if picking.despatch_id and picking.despatch_id.state=='open':
						self.env['account.move.l10n_pe_transportref'].create({
								'move_id':new_invoice.id,
								'ref_number':picking.despatch_id.name,
								'ref_type':'09'
							})
			productos = {}
			if self.picking_ids.ids:
				for line_picking in self.picking_ids.mapped('move_ids_without_package'):
					if line_picking.state == 'done':
						if line_picking.product_id.id in productos:
							productos[line_picking.product_id.id] = productos[line_picking.product_id.id] + line_picking.quantity
						else:
							productos[line_picking.product_id.id] = line_picking.quantity

				for line_invoice in new_invoice.invoice_line_ids:
					if line_invoice.product_id.type != 'service':
						if line_invoice.product_id.id in productos and line_invoice.quantity > productos[line_invoice.product_id.id]:
							line_invoice.quantity = productos[line_invoice.product_id.id]
						elif line_invoice.product_id.id in productos:
							pass
						else:
							line_invoice.unlink()
				#new_invoice._onchange_invoice_line_ids()
			#new_invoice._recompute_tax_lines()
			#new_invoice._onchange_invoice_line_ids()
			#new_invoice._onchange_tc_per()
			#_recompute_cash_rounding_lines ese pareciera ser no revisa a fondo ya que calculaba bien
		return res
