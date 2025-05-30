# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import *
from datetime import timedelta


class sql_kardex(models.Model):
	_inherit ='sql.kardex'

	def _have_mrp(self):
		return True

class stock_move_line(models.Model):
	_inherit = 'stock.move.line'

	def edit_kardex_date(self):
		return {			
			'name':u'Editar Fecha Kardex',
			'res_id':self.id,
			'view_mode': 'form',
			'res_model': 'stock.move.line',
			'view_id': self.env.ref("mrp_kardex.move_line_fecha_kardex").id,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}


	def edit_mostrar_no(self):
		return {			
			'name':u'Editar No Mostrar en Kardex',
			'res_id':self.id,
			'view_mode': 'form',
			'res_model': 'stock.move.line',
			'view_id': self.env.ref("mrp_kardex.move_line_no_mostrar").id,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}


class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	kardex_date = fields.Datetime(string="Fecha Kardex",copy=False)
	no_mostrar = fields.Boolean('No Mostrar en Kardex', copy=False)
	operation_type_sunat_consume = fields.Many2one('type.operation.kardex', string="Tipo de Operacion Sunat Consumo")
	operation_type_sunat_fp = fields.Many2one('type.operation.kardex', string="Tipo de Operacion Sunat Producto Terminado")


	def write(self,vals):
		t = super(MrpProduction,self).write(vals)
		if 'kardex_date' in vals:
			self.update_kardex_dates()
		return t

	def update_kardex_dates(self):
		for i in self:
			if not i.kardex_date:
				i.kardex_date = datetime.now()
			move_line_ids = self.env['stock.move.line'].search(['|', ('move_id.raw_material_production_id', '=', i.id), ('move_id.production_id', '=', i.id)])
			for moves_line in move_line_ids:
				if moves_line.move_id.id:
					moves_line.move_id.with_context({'permitido':1}).write({'kardex_date': i.kardex_date })
			for elem in self.env['stock.move.line'].search([('move_id.production_id', '=', i.id)]):
				if elem.move_id.id:
					elem.move_id.with_context({'permitido':1}).write({'kardex_date':i.kardex_date + timedelta(seconds=1)})
			move_line_ids.with_context({'permitido':1}).write({'kardex_date': i.kardex_date })
			for elem in self.env['stock.move.line'].search([('move_id.production_id', '=', i.id)]):
				elem.with_context({'permitido':1}).write({'kardex_date':i.kardex_date + timedelta(seconds=1)})
			

	def button_mark_done(self):
		#self.ensure_one()
		error = ''
		#for line in self.move_raw_ids:
		#	if line.quantity > line.forecast_availability:
		#		raise UserError('Las cantidades consumidas no pueden ser mayor a lo reservado')

		t = super(MrpProduction, self).button_mark_done()

		return t


	@api.depends(
		'move_raw_ids.state', 'move_raw_ids.quantity', 'move_finished_ids.state',
		'workorder_ids.state', 'product_qty', 'qty_producing', 'move_raw_ids.picked')
	def _compute_state(self):
		t = super(MrpProduction,self)._compute_state()
		all_lines = True
		for i in self.move_raw_ids:
			if i.state not in ('done','cancel'):
				all_lines = False
			
		for i in self.move_finished_ids:
			if i.state not in ('done','cancel'):
				all_lines = False

		if all_lines and len(self.move_raw_ids)>0 and len(self.move_finished_ids)>0:
			self.update_kardex_dates()
			self.costeo_mrp()
		return t



	def costeo_mrp(selfs):
		for self in selfs:
			import datetime
			from datetime import timedelta
			productos = self.env['stock.move.line'].search(['|', ('move_id.raw_material_production_id', '=', self.id), ('move_id.production_id', '=', self.id)]).mapped('product_id')
			moves = self.env['stock.move.line'].search(['|', ('move_id.raw_material_production_id', '=', self.id), ('move_id.production_id', '=', self.id)]).mapped('move_id')
			posible_fecha = self.env["kardex.cerrado.config"].sudo().search([("company_id","=",self.env.company.id)], limit=1, order="fecha_fin desc")
			fecha = False
			if posible_fecha.id:
				fecha = posible_fecha.fecha_fin + timedelta(days=1)
			if not fecha:
				posible_fecha = self.env["stock.move"].sudo().search([("picking_id.company_id","=",self.env.company.id),("state","=",'done')], limit=1, order="kardex_date")
				if posible_fecha.id:
					fecha = (posible_fecha.kardex_date - timedelta(hours=5)).date()
			mes = str(fecha.month if fecha else (datetime.datetime.now() - timedelta(hours=5)).date().month)
			nuevo = self.env['valor.unitario.kardex'].with_context(force_company=self.env.company.id).create({'fecha_inicio': str(fecha) if fecha else str(datetime.datetime.now())[0:4]+ '-'+mes+'-01', 'fecha_final': str(datetime.datetime.now())[0:4]+'-12-31' })
			nuevo.with_context(force_company=self.env.company.id,product_ids =productos.ids).do_valor()
			self.env['stock.valuation.layer'].search([('stock_move_id','in',moves.ids)]).get_value()
	


class MRP_unbuild(models.Model):
	_inherit= 'mrp.unbuild'

	def action_validate(self):
		t = super(MRP_unbuild,self).action_validate()


		for i in self:
			move_line_ids = self.env['stock.move.line'].search(['|', ('move_id.consume_unbuild_id', '=', i.id), ('move_id.unbuild_id', '=', i.id)])
			move_line_ids.with_context({'permitido':1}).write({'kardex_date': datetime.now() })
			move_line_ids.mapped('move_id').with_context({'permitido':1}).write({'no_mostrar':True})
			for elem in self.env['stock.move.line'].search([('move_id.unbuild_id', '=', i.id)]):
				elem.with_context({'permitido':1}).write({'kardex_date':datetime.now() - timedelta(seconds=1)})
			
			move_line_ids = self.env['stock.move.line'].search(['|', ('move_id.raw_material_production_id', '=', i.mo_id.id), ('move_id.production_id', '=', i.mo_id.id)])
			for moves_line in move_line_ids:
				if moves_line.move_id.id:
					moves_line.move_id.with_context({'permitido':1}).write({'no_mostrar': True })	

		return t




from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_round


class stock_valuation_layer(models.Model):
	_inherit = 'stock.valuation.layer'

	price_unit_it = fields.Float(related='stock_move_id.price_unit_it')
	value = fields.Float(compute="get_value",store=True)

	@api.depends('stock_move_id.price_unit_it','unit_cost','quantity','stock_move_id.state')
	def get_value(self):
		for i in self:
			i.stock_move_id.read()
			i.value = i.price_unit_it * abs(i.quantity)


class MrpCostStructure(models.AbstractModel):
	_inherit = 'report.mrp_account_enterprise.mrp_cost_structure'
	_description = 'MRP Cost Structure Report'

	def get_lines(self, productions):
		ProductProduct = self.env['product.product']
		StockMove = self.env['stock.move']
		res = []
		currency_table = self.env['res.currency']._get_query_currency_table(self.env.companies.ids, fields.Date.today())
		for product in productions.mapped('product_id'):
			mos = productions.filtered(lambda m: m.product_id == product)
			# variables to calc cost share (i.e. between products/byproducts) since MOs can have varying distributions
			total_cost_by_mo = defaultdict(float)
			component_cost_by_mo = defaultdict(float)
			operation_cost_by_mo = defaultdict(float)

			# Get operations details + cost
			operations = []
			total_cost_operations = 0.0
			Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
			if Workorders:
				total_cost_operations = self._compute_mo_operation_cost(currency_table, Workorders, total_cost_by_mo, operation_cost_by_mo, total_cost_operations, operations)

			# Get the cost of raw material effectively used
			raw_material_moves = {}
			total_cost_components = 0.0
			query_str = """SELECT
								sm.product_id,
								mo.id,
								abs(SUM(sm.quantity)),
								abs(SUM(coalesce(sm.price_unit_it,0)*abs(svl.quantity) )),
								coalesce(currency_table.rate,1)
							 FROM stock_move AS sm
					   INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
					   LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
					   LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
							WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
						 GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table,)
			self.env.cr.execute(query_str, (tuple(mos.ids), ))
			for product_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
				cost *= currency_rate
				if product_id in raw_material_moves:
					product_moves = raw_material_moves[product_id]
					product_moves['cost'] += cost
					product_moves['qty'] += qty
				else:
					raw_material_moves[product_id] = {
					'qty': qty,
					'cost': cost,
					'product_id': ProductProduct.browse(product_id),
				}
				total_cost_by_mo[mo_id] += cost
				component_cost_by_mo[mo_id] += cost
				total_cost_components += cost
			raw_material_moves = list(raw_material_moves.values())
			# Get the cost of scrapped materials
			scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])

			# Get the byproducts and their total + avg per uom cost share amounts
			total_cost_by_product = defaultdict(float)
			qty_by_byproduct = defaultdict(float)
			qty_by_byproduct_w_costshare = defaultdict(float)
			component_cost_by_product = defaultdict(float)
			operation_cost_by_product = defaultdict(float)
			# tracking consistent uom usage across each byproduct when not using byproduct's product uom is too much of a pain
			# => calculate byproduct qtys/cost in same uom + cost shares (they are MO dependent)
			byproduct_moves = mos.move_byproduct_ids.filtered(lambda m: m.state != 'cancel')
			for move in byproduct_moves:
				qty_by_byproduct[move.product_id] += move.product_qty
				# byproducts w/o cost share shouldn't be included in cost breakdown
				if move.cost_share != 0:
					qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
					cost_share = move.cost_share / 100
					total_cost_by_product[move.product_id] += total_cost_by_mo[move.production_id.id] * cost_share
					component_cost_by_product[move.product_id] += component_cost_by_mo[move.production_id.id] * cost_share
					operation_cost_by_product[move.product_id] += operation_cost_by_mo[move.production_id.id] * cost_share

			# Get product qty and its relative total + avg per uom cost share amount
			uom = product.uom_id
			mo_qty = 0
			for m in mos:
				cost_share = float_round(1 - sum(m.move_finished_ids.mapped('cost_share')) / 100, precision_rounding=0.0001)
				total_cost_by_product[product] += total_cost_by_mo[m.id] * cost_share
				component_cost_by_product[product] += component_cost_by_mo[m.id] * cost_share
				operation_cost_by_product[product] += operation_cost_by_mo[m.id] * cost_share
				mo_qty += sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_qty'))
			res.append({
				'product': product,
				'mo_qty': mo_qty,
				'mo_uom': uom,
				'operations': operations,
				'currency': self.env.company.currency_id,
				'raw_material_moves': raw_material_moves,
				'total_cost_components': total_cost_components,
				'total_cost_operations': total_cost_operations,
				'total_cost': total_cost_components + total_cost_operations,
				'scraps': scraps,
				'mocount': len(mos),
				'byproduct_moves': byproduct_moves,
				'component_cost_by_product': component_cost_by_product,
				'operation_cost_by_product': operation_cost_by_product,
				'qty_by_byproduct': qty_by_byproduct,
				'qty_by_byproduct_w_costshare': qty_by_byproduct_w_costshare,
				'total_cost_by_product': total_cost_by_product
			})
		return res

	@api.model
	def _get_report_values(self, docids, data=None):
		productions = self.env['mrp.production']\
			.browse(docids)\
			.filtered(lambda p: p.state != 'cancel')
		res = None
		if all(production.state == 'done' for production in productions):
			res = self.get_lines(productions)
		return {'lines': res}

	def _compute_mo_operation_cost(self, currency_table, Workorders, total_cost_by_mo, operation_cost_by_mo, total_cost_operations, operations):
		query_str = """  SELECT
						wo.production_id,
						wo.id,
						op.id,
						wo.name,
						wc.name,
						wo.duration,
						CASE WHEN wo.costs_hour = 0.0 THEN wc.costs_hour ELSE wo.costs_hour END AS costs_hour,
						currency_table.rate
					FROM mrp_workcenter_productivity t
					LEFT JOIN mrp_workorder wo ON (wo.id = t.workorder_id)
					LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id)
					LEFT JOIN mrp_routing_workcenter op ON (wo.operation_id = op.id)
					LEFT JOIN {currency_table} ON currency_table.company_id = t.company_id
					WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
					GROUP BY wo.production_id, wo.id, op.id, wo.name, wc.costs_hour, wc.name, currency_table.rate
					ORDER BY wo.name, wc.name
				""".format(currency_table=currency_table,)
		self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
		for mo_id, dummy_wo_id, op_id, wo_name, wc_name, duration, cost_hour, currency_rate in self.env.cr.fetchall():
			cost = duration / 60.0 * cost_hour * currency_rate
			total_cost_by_mo[mo_id] += cost
			operation_cost_by_mo[mo_id] += cost
			total_cost_operations += cost
			operations.append([wc_name, op_id, wo_name, duration / 60.0, cost_hour * currency_rate])

		return total_cost_operations


class ProductTemplateCostStructure(models.AbstractModel):
	_name = 'report.mrp_account_enterprise.product_template_cost_structure'
	_description = 'Product Template Cost Structure Report'

	@api.model
	def _get_report_values(self, docids, data=None):
		productions = self.env['mrp.production'].search([('product_id', 'in', docids), ('state', '=', 'done')])
		res = self.env['report.mrp_account_enterprise.mrp_cost_structure'].get_lines(productions)
		return {'lines': res}


