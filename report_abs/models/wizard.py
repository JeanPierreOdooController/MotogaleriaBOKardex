# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import tools
from datetime import *
from odoo.exceptions import UserError
import base64
import datetime
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from odoo.osv import osv
import codecs

#class wizard_saleparticipation_report(models.Model):
#	_name = 'wizard.saleparticipation.report'
class abc_wizard_report(models.TransientModel):
	_name = "abc.wizard.report"
	_description = "Reporte ABC"

	import_product_type = fields.Selection([('rotation','Rotación/Entregados'),('ganancia','Ganancia/Margen'),('precio','Precio Venta')],string='Tipo de Operacion', required=True,default="rotation")
	company_id = fields.Many2one('res.company',string=u'Compañia',required=True, default=lambda self: self.env.company,readonly=True)
	fecha_in = fields.Date(string="Fecha Inicio")
	fecha_fin = fields.Date(string="Fecha Fin")
	fecha_in_mod = fields.Date(string="Fecha Inicio Mod")
	fecha_fin_mod = fields.Date(string="Fecha Fin Mod")
 
	def do_csvtoexcel(self):
		cad = ""
		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
		lst_locations = locat_ids.ids
		productos='('
		almacenes='('
		import datetime
		fecha_hoy = str(datetime.datetime.now())[:10]
		fecha_inicial = fecha_hoy[:4] + '-01-01'
		fecha_fin=fecha_hoy
		date_ini=fecha_inicial
		date_fin=fecha_fin
		self.fecha_in_mod = date_ini
		date_ini=self.fecha_in_mod
		self.fecha_fin_mod = date_fin
		date_fin=self.fecha_fin_mod
		lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+')'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+')'
		import datetime		

		config = self.env['kardex.parameter'].search([('company_id','=',self.company_id.id)])

		date_ini = '%d-01-01' % ( config._get_anio_start(date_fin.year) )

		kardex_save_obj = False
		kardex_save_obj = self.env['kardex.save'].search([('company_id','=',self.company_id.id),('state','=','done'),('name.date_end','<',self.fecha_in_mod)]).sorted(lambda l: l.name.code , reverse=True)
		if len(kardex_save_obj)>0:
			kardex_save_obj = kardex_save_obj[0]
			date_ini = kardex_save_obj.name.date_end + timedelta(days=1)
		si_existe = ""
		if kardex_save_obj:
			si_existe = """union all


select 
				ksp.producto as product_id,
				ksp.almacen as location_id,
				'' as origen_usage,
				sl.usage as destino_usage,
				ksp.cprom * ksp.stock as debit,
				0 as credit,
				(fecha || ' 00:00:00')::timestamp as fechax,
				'' as type_doc,
				'' as serial,
				'' as nro,
				'' as numdoc_cuadre,
				'' as nro_documento,
				'Saldo Inicial' as name,
				'' as operation_type,
				pname.new_name,
				coalesce(pp.default_code,pt.default_code) as default_code,
				uu.name as unidad,
				ksp.stock as ingreso,
				0 as salida,
				ksp.cprom as cadquiere,
				'' as origen,
				sl.complete_name as destino,
				sl.complete_name as almacen,
				pb.name as marca_prod

			from kardex_save_period ksp 
			inner join stock_location sl on sl.id = ksp.almacen
			inner join product_product pp on pp.id = ksp.producto
			inner join product_template pt on pt.id = pp.product_tmpl_id
			inner join uom_uom uu on uu.id = pt.uom_id
			inner join product_category pc on pc.id = pt.categ_id
			left join stock_production_lot spt on spt.id = ksp.lote
			left join product_brand pb on pb.id= pt.product_brand_id
			 LEFT JOIN ( SELECT t_pp.id,
					((     (max(t_pt.name->>'es_PE'::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
				   FROM product_product t_pp
					 JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
					 LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
					 LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
					 LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
				  GROUP BY t_pp.id) pname ON pname.id = pp.id
			 where save_id = """+str(kardex_save_obj.id)+"""
			 """
		total_all = []
		self.env.cr.execute("""  
					select  
					product_id,
					location_id,
					origen_usage,
					destino_usage,
					debit,
					credit,
					fechax,
					type_doc,
					serial,
					nro,
					numdoc_cuadre,
					nro_documento,
					name,
					operation_type,
					new_name,
					default_code,
					unidad,
					ingreso,
					salida,
					cadquiere,
					origen,
					destino,
					almacen,
					marca_prod
			 from (
					select 
					product_id,
					location_id,
					origen_usage,
					destino_usage,
					debit,
					credit,
					fechax,
					type_doc,
					serial,
					nro,
					numdoc_cuadre,
					nro_documento,
					name,
					operation_type,
					new_name,
					default_code,
					unidad,
					ingreso,
					salida,
					cadquiere,
					origen,
					destino,
					almacen,
					marca_prod
					from (
		select vst_kardex_sunat.*,sp.name as doc_almac,sm.kardex_date as fecha_albaran,
		vst_kardex_sunat.fecha - interval '5' hour as fechax,sl_o.usage as origen_usage , sl_d.usage as destino_usage, np.new_name, pb.name as marca_prod
					from vst_kardex_fisico_valorado as vst_kardex_sunat
		left join stock_move sm on sm.id = vst_kardex_sunat.stock_moveid
		left join stock_picking sp on sp.id = sm.picking_id

							inner join stock_location sl_o on sl_o.id = sm.location_id
							inner join stock_location sl_d on sl_d.id = sm.location_dest_id
		left join (
			select t_pp.id, 
					t_pt.product_brand_id as marca,
					((     (max(t_pt.name->>'es_PE'::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
				   FROM product_product t_pp
					 JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
				left join product_variant_combination pvc on pvc.product_product_id = t_pp.id
				left join product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
				left join product_attribute_value pav on pav.id = ptav.product_attribute_value_id
				group by t_pp.id, t_pt.product_brand_id
				) np on np.id = vst_kardex_sunat.product_id
		left join product_brand pb on pb.id= np.marca
							
			   where (fecha_num((vst_kardex_sunat.fecha - interval '5' hour)::date) between """+str(date_ini).replace('-','')+""" and """+str(date_fin).replace('-','')+""")    
			   and vst_kardex_sunat.location_id in """+str(almacenes)+""" and vst_kardex_sunat.product_id in """ +str(productos)+ """
					 and vst_kardex_sunat.company_id = """ +str(self.company_id.id)+ """
					order by vst_kardex_sunat.location_id,vst_kardex_sunat.product_id,vst_kardex_sunat.fecha,vst_kardex_sunat.esingreso,vst_kardex_sunat.stock_moveid,vst_kardex_sunat.nro
					)Total   """+si_existe+"""			
	) A order by location_id,product_id,fechax
					
				""")
		total_all = self.env.cr.fetchall()
		cont_report = 0
		import datetime
		dicc_guardado={}
		tiempo_inicial = datetime.datetime.now()
		tiempo_pasado = [0,0]
		cprom_data = {}

		ingreso1 =0
		ingreso2 =0
		salida1 =0
		salida2 =0
		producto = 0
		almacen = 0
		array_grabar = None
		flag = False
		for xl in total_all:
			l = {
			'product_id':xl[0],
			'location_id':xl[1],
			'origen_usage':xl[2],
			'destino_usage':xl[3],
			'debit':xl[4],
			'credit':xl[5],
			'fechax':xl[6],
			'type_doc':xl[7],
			'serial':xl[8],
			'nro':xl[9],
			'numdoc_cuadre':xl[10],
			'nro_documento':xl[11],
			'name':xl[12],
			'operation_type':xl[13],
			'new_name':xl[14],
			'default_code':xl[15],
			'unidad':xl[16],
			'ingreso':xl[17],
			'salida':xl[18],
			'cadquiere':xl[19],
			'origen':xl[20],
			'destino':xl[21],
			'almacen':xl[22],
			'marca_prod':xl[23],
			}

			if producto == None:
				producto = l['product_id']
				almacen = l['almacen']
			if producto != 	l['product_id'] or almacen != l['almacen']:
				producto = l['product_id']
				almacen = l['almacen']	
				if array_grabar:
					if array_grabar[0] in dicc_guardado:
						saldo_antiguo = float(dicc_guardado[array_grabar[0]]["saldo_cantidad"])
						saldo_antiguo+= cprom_acum[0] if len(cprom_acum)>1 and cprom_acum[0] else 0
						dicc_guardado[array_grabar[0]]["saldo_cantidad"] = saldo_antiguo
						saldo_soles = float(dicc_guardado[array_grabar[0]]["saldo_soles"])
						saldo_soles +=cprom_acum[1] if len(cprom_acum)>1 and cprom_acum[1] else 0
						dicc_guardado[array_grabar[0]]["saldo_soles"] = saldo_soles
					else:
						dicc_guardado[array_grabar[0]]={
							"default_code":array_grabar[1] if array_grabar[1] else '',
							"producto":  array_grabar[2] if array_grabar[2] else '' ,
							"entregado":0,
							"unidad_medida":'',
							"costo_total":0,
							"precio_total":0,
							"marca":str(array_grabar[6] if array_grabar[6] else ""),
							"margen":0,
							"acumulado":0,
							"grupo":"Grupo D",
							"saldo_cantidad":array_grabar[4] if array_grabar[4] else 0,
							"udm":array_grabar[3] if array_grabar[3] else "",
							"saldo_soles":array_grabar[5] if array_grabar[5] else 0
						}
			cont_report += 1
			llave = (l['product_id'],l['location_id'])
			cprom_acum = [0,0]
			if llave in cprom_data:
				cprom_acum = cprom_data[llave]
			else:
				cprom_data[llave] = cprom_acum

			cprom_act_antes = cprom_data[llave][1] / cprom_data[llave][0] if cprom_data[llave][0] != 0 else 0

			data_temp = {}
			
			data_temp = {'origen':l['origen_usage'] or '','destino':l['destino_usage'] or ''}
			ingreso_v = 0
			egreso_v = 0
			if l['ingreso'] or l['debit']:
				if (data_temp['origen'] == 'internal' and data_temp['destino'] == 'internal') or (data_temp['origen'] == 'transit' and data_temp['destino'] == 'internal'):
					cprom_acum[0] = cprom_acum[0] + (l['ingreso'] if l['ingreso'] else 0) -  (l['salida'] if l['salida'] else 0)
					cprom_acum[1] = cprom_acum[1] + (l['debit'] if l['debit'] else 0) -  (l['credit'] if l['credit'] else 0)

					ingreso_v = (l['debit'] if l['debit'] else 0) 
				else:	
					cprom_acum[0] = cprom_acum[0] + (l['ingreso'] if l['ingreso'] else 0) -  (l['salida'] if l['salida'] else 0)
					cprom_acum[1] = cprom_acum[1] + (l['debit'] if l['debit'] else 0) -  (l['credit'] if l['credit'] else 0)

					ingreso_v = (l['debit'] if l['debit'] else 0) 
			else:
				if (data_temp['origen'] == 'internal' and data_temp['destino'] == 'supplier'):
					cprom_acum[0] = cprom_acum[0] -  (l['salida'] if l['salida'] else 0)
					cprom_acum[1] = cprom_acum[1] - (l['debit'] if l['debit'] else 0) - ( (l['credit'] if l['credit'] else 0) * (l['salida'] if l['salida'] else 0) )
					egreso_v = (l['credit'] if l['credit'] else 0) * (l['salida'] if l['salida'] else 0)
				else:
					if l['salida']:
						cprom_acum[0] = cprom_acum[0] + (l['ingreso'] if l['ingreso'] else 0) -  (l['salida'] if l['salida'] else 0)
						cprom_acum[1] = cprom_acum[1] - (l['salida'] if l['salida'] else 0)*(cprom_act_antes if cprom_act_antes else 0)

						egreso_v = (l['salida'] if l['salida'] else 0)*(cprom_act_antes if cprom_act_antes else 0)
					else:
						cprom_acum[0] = cprom_acum[0] + (l['ingreso'] if l['ingreso'] else 0) -  (l['salida'] if l['salida'] else 0)
						cprom_acum[1] = cprom_acum[1] - (l['credit'] if l['credit'] else 0)

						egreso_v = (l['credit'] if l['credit'] else 0)

			cprom_act = cprom_acum[1] / cprom_acum[0] if cprom_acum[0] != 0 else 0

			cprom_data[llave] = cprom_acum

			linea = []
			producto_obj = self.env['product.product'].browse(l['product_id'])
			linea.append(producto_obj.id)
			linea.append( l['default_code'] if l['default_code'] else '')
			linea.append( l['new_name'] if l['new_name'] else '' )
			linea.append( l['unidad'] if l['unidad'] else '' )

			linea.append( cprom_acum[0] if len(cprom_acum)>1 and cprom_acum[0] else 0 )
			linea.append( cprom_acum[1] if len(cprom_acum)>1 and cprom_acum[1] else 0 )
			linea.append( l['marca_prod'] if l['marca_prod'] else '' )
			array_grabar = linea.copy()

			ingreso1 += l['ingreso'] or 0
			ingreso2 += ingreso_v or 0
			salida1 += l['salida'] or 0
			salida2 += egreso_v or 0
			#if producto_obj.id==81205:
				#raise UserError((l['default_code'] if l['default_code'] else '') + (str(cprom_acum[0] if len(cprom_acum)>1 and cprom_acum[0] else 0))+"   -   soles"+(str(cprom_acum[1] if len(cprom_acum)>1 and cprom_acum[1] else 0)))
		if array_grabar:
			if array_grabar[0] in dicc_guardado:
				saldo_antiguo = float(dicc_guardado[array_grabar[0]]["saldo_cantidad"])
				saldo_antiguo+= cprom_acum[0] if len(cprom_acum)>1 and cprom_acum[0] else 0
				dicc_guardado[array_grabar[0]]["saldo_cantidad"] = saldo_antiguo
				saldo_soles = float(dicc_guardado[array_grabar[0]]["saldo_soles"])
				saldo_soles +=cprom_acum[1] if len(cprom_acum)>1 and cprom_acum[1] else 0
				dicc_guardado[array_grabar[0]]["saldo_soles"] = saldo_soles
			else:
				dicc_guardado[array_grabar[0]]={
					"default_code":array_grabar[1] if array_grabar[1] else '',
					"producto":  array_grabar[2] if array_grabar[2] else '' ,
					"entregado":0,
					"unidad_medida":'',
					"costo_total":0,
					"precio_total":0,
					"margen":0,
					"marca":str(array_grabar[6] if array_grabar[6] else ""),
					"acumulado":0,
					"grupo":"Grupo D",
					"saldo_cantidad":array_grabar[4] if array_grabar[4] else 0,
					"udm":array_grabar[3] if array_grabar[3] else "",
					"saldo_soles":array_grabar[5] if array_grabar[5] else 0
				}
  
  
  
		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]

		import io
		from xlsxwriter.workbook import Workbook
		#recordatorio me dijeron el total cantidad no por el promedio de costo sino sumatoria ver si es logico
		if self.import_product_type=="rotation":
			self.env.cr.execute("""
		select 
			pp.default_code as default_code, 
			pname.new_name as producto,
			sml.product_uom_id as unidad_medida_entregado,
			sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) ) as costo_total,
			sum(coalesce(sml.quantity,0)) as entregas_total,
			sum(   CASE 
						WHEN rc.name='PEN' 
					   		then coalesce(sol.price_unit ,  0      ) 
						ELSE 
					   		coalesce(sol.price_unit ,   0   ) *coalesce(tc.sale_type,1)  
						END * 
					   	coalesce(sml.quantity,0)) as facturado_precio_total,


			(sum
				(   
					CASE 
						WHEN rc.name='PEN' 
							then coalesce(sol.price_unit ,  0     ) 
						ELSE coalesce(sol.price_unit ,  0      ) * coalesce(tc.sale_type,1)  
					END * coalesce(sml.quantity,0))) -
					(sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) )) as margen_tt,

			sml.product_id as product_id,
			pb.name as marca
			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking spc on sml.picking_id = spc.id

					   

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id

				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id
				left join res_currency_rate tc on tc.name = (  so.date_order  - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""

				inner join product_product pp on sml.product_id=pp.id
				inner join product_template pt on pt.id = pp.product_tmpl_id
				left join product_brand pb on pb.id = pt.product_brand_id
						LEFT JOIN ( SELECT t_pp.id,
							((     (max(t_pt.name->>'es_PE'::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
						FROM product_product t_pp
							JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
							LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
							LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
							LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
						   GROUP BY t_pp.id) pname ON pname.id = pp.id


					where 
sol.id is not null  and
spc.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' 
and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
						group by sml.product_id, sml.product_uom_id, pname.new_name, pp.default_code, pb.name
							order by entregas_total desc;
							""")
			cnslta = self.env.cr.dictfetchall()


			contador = 0
			output = io.BytesIO()
			workbook = Workbook(output, {'constant_memory': False})
			worksheet = workbook.add_worksheet("Reporte ABC")
			worksheet.set_column('A:A', 27)
			worksheet.set_column('B:B', 59)
			worksheet.set_column('C:C', 18.5)
			worksheet.set_column('D:D', 17.5)
			worksheet.set_column('E:E', 19)
			worksheet.set_column('F:F', 18.5)
			worksheet.set_column('G:G', 17.5)
			worksheet.set_column('H:H', 18.5)
			worksheet.set_column('I:I', 18.5)
			worksheet.set_column('J:J', 17.5)
			worksheet.set_column('K:K', 17.5)
			worksheet.set_column('L:L', 17.5)

			cell_titulo_bottom = workbook.add_format({'bold': True})
			cell_titulo_bottom.set_align('center')
			cell_titulo_bottom.set_font_name('Calibri')
			cell_titulo_bottom.set_font_size(26)
			cell_titulo_bottom.set_font_color('#2D45F3')


			cell_subtitle = workbook.add_format({'bold': True})
			cell_subtitle.set_align('center')
			cell_subtitle.set_bottom(1)
			cell_subtitle.set_top(1)
			cell_subtitle.set_left(1)
			cell_subtitle.set_right(1)
			cell_subtitle.set_font_name('Calibri')
			cell_subtitle.set_font_size(14)
			cell_subtitle.set_bg_color('#F3F5F5')


			cell_subtitle_sub = workbook.add_format({'bold': True})
			cell_subtitle_sub.set_align('left')
			cell_subtitle_sub.set_font_name('Calibri')
			cell_subtitle_sub.set_font_size(14)




			cell_texto_bottom_nta = workbook.add_format({'bold': False})
			cell_texto_bottom_nta.set_align('left')
			cell_texto_bottom_nta.set_bottom(1)
			cell_texto_bottom_nta.set_top(1)
			cell_texto_bottom_nta.set_left(1)
			cell_texto_bottom_nta.set_right(1)
			cell_texto_bottom_nta.set_font_name('Calibri')
			cell_texto_bottom_nta.set_font_size(12)
			

			cell_texto_numerotres = workbook.add_format({'bold': False})
			cell_texto_numerotres.set_align('right')
			cell_texto_numerotres.set_bottom(1)
			cell_texto_numerotres.set_top(1)
			cell_texto_numerotres.set_left(1)
			cell_texto_numerotres.set_right(1)
			cell_texto_numerotres.set_font_name('Calibri')
			cell_texto_numerotres.set_font_size(12)
			cell_texto_numerotres.set_num_format('0.000')

			cell_texto_numerodos = workbook.add_format({'bold': False})
			cell_texto_numerodos.set_align('right')
			cell_texto_numerodos.set_bottom(1)
			cell_texto_numerodos.set_top(1)
			cell_texto_numerodos.set_left(1)
			cell_texto_numerodos.set_right(1)
			cell_texto_numerodos.set_font_name('Calibri')
			cell_texto_numerodos.set_font_size(12)
			cell_texto_numerodos.set_num_format('0.00')

			worksheet.merge_range('A2:H4', str(self.company_id.name), cell_titulo_bottom)
			worksheet.write('A6', "Modalidad:", cell_subtitle_sub)
			worksheet.write('B6', "Rotación/Entregados" if self.import_product_type=='rotation'else "Ganancia/Precio", cell_subtitle_sub)
			worksheet.write('A7', "Fecha Inicio:", cell_subtitle_sub)
			worksheet.write('B7', str(self.fecha_in), cell_subtitle_sub)
			worksheet.write('A8', "Fecha Fin:", cell_subtitle_sub)
			worksheet.write('B8', str(self.fecha_fin), cell_subtitle_sub)

			worksheet.write('A10', "Codigo Producto", cell_subtitle)
			worksheet.write('B10', "Producto", cell_subtitle)
			worksheet.write('C10', "Marca", cell_subtitle)
			worksheet.write('D10', "Entregado", cell_subtitle)
			worksheet.write('E10', "UDM Entregado", cell_subtitle)
			worksheet.write('F10', "Costo Total", cell_subtitle)
			worksheet.write('G10', "Precio Total", cell_subtitle)
			worksheet.write('H10', "Margen", cell_subtitle)
			worksheet.write('I10', "% Acumulado", cell_subtitle)
			worksheet.write('J10', "Grupo", cell_subtitle)
			worksheet.write('K10', "Saldo Cantidad", cell_subtitle)
			worksheet.write('L10', "UDM", cell_subtitle)
			worksheet.write('M10', "Saldo Soles", cell_subtitle)
			
			margenes_totales = 0

			self.env.cr.execute("""select 
				sum(coalesce(sml.quantity,0)) as entregas_total
			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking spc on sml.picking_id = spc.id

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id

				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id

				left join res_currency_rate tc on tc.name = (   so.date_order - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""

				inner join product_product pp on sml.product_id=pp.id
					where 
sol.id is not null and
spc.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
					;
							""")

#REVISAR
			prueba_consulta = self.env.cr.dictfetchall()
			margenes_totales=float(prueba_consulta[0]["entregas_total"])
#			for x in cnslta:
#				margenes_totales+=x["entregas_total"]
			linea = 10
			grupo_a = 80
			grupo_b = 90
			acumulado_porcetaje = 0
			for x in cnslta:
				acumulado_porcetaje +=  (((x["entregas_total"] if x["entregas_total"] else 0)*100)/margenes_totales) if margenes_totales!=0 else 100
				udm_entregado = self.env["uom.uom"].sudo().browse(x["unidad_medida_entregado"])
				producto_obj = self.env['product.product'].browse(x['product_id'])
				#del sub
				#producto
				#unidad_medida
				#saldo_cantidad
				#saldo_soles
				linea += 1
				if acumulado_porcetaje <= grupo_a:
					grupo="Grupo A"
					worksheet.write('A'+str(linea), x["default_code"] if x["default_code"] else "",cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_numerotres)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_tt"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje <= grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo B"
					worksheet.write('A'+str(linea), x["default_code"] if x["default_code"] else "",cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_numerotres)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_tt"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje > grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo C"
					worksheet.write('A'+str(linea), x["default_code"] if x["default_code"] else "",cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_numerotres)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_tt"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				if producto_obj.id in dicc_guardado:
					dicc_guardado.pop(producto_obj.id)
			for resto in dicc_guardado:
				linea += 1
				grupo="Grupo D"
				worksheet.write('A'+str(linea), dicc_guardado[resto]["default_code"] if "default_code" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('B'+str(linea), dicc_guardado[resto]["producto"] if "producto" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('C'+str(linea), dicc_guardado[resto]["marca"] if "marca" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('D'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('E'+str(linea), "",cell_texto_bottom_nta)
				worksheet.write('F'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('G'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('H'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('I'+str(linea), 0,cell_texto_numerodos)
				worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
				worksheet.write('K'+str(linea), dicc_guardado[resto]["saldo_cantidad"] if "saldo_cantidad" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				worksheet.write('L'+str(linea), dicc_guardado[resto]["udm"] if "udm" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('M'+str(linea), dicc_guardado[resto]["saldo_soles"] if "saldo_soles" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				
				producto_obj = self.env['product.product'].browse(resto)
			linea +=1
			worksheet.write('D'+str(linea), margenes_totales,cell_texto_numerotres)
			workbook.close()
			output.seek(0)

			output_datas = base64.b64encode(output.getvalue())
			output.close()

			return self.env['popup.it'].get_file('Reporte ABC Rotración-Entregados.xlsx',output_datas)

			attach_id = self.env['ir.attachment'].create({
					'name': "Reporte ABC Rotación-Entregados.xlsx",
					'type': 'binary',
					'datas': base64.b64encode(output.read()),
					'eliminar_automatico': True
				})
			output.close()

			
			return {
				'type': 'ir.actions.client',
				'tag': 'notification_llikha',
				'params': {
					'title':'Reporte ABC',
					'type': 'success',
					'sticky': True,
					'message': 'Se Proceso Exitosamente',
					'next': {'type': 'ir.actions.act_window_close'},
					'buttons':[{
						'label':'Descargar Kardex Valorado',
						'model':'ir.attachment',
						'method':'get_download_ls',
						'id':attach_id.id,
						}
					],
				}
			}



		if self.import_product_type=="ganancia":
			self.env.cr.execute("""select 
pp.default_code as default_code, 
pname.new_name as producto,
sml.product_uom_id as unidad_medida_entregado,
sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) ) as costo_total,
sum(coalesce(sml.quantity,0)) as entregas_total,

sum(   CASE 
			WHEN rc.name='PEN' 
				then coalesce(sol.price_unit ,0) 
			ELSE coalesce(sol.price_unit ,0)*coalesce(tc.sale_type,1)  
			END * coalesce(sml.quantity,0)) as facturado_precio_total,

(sum(   CASE 
			WHEN rc.name='PEN' 
				then coalesce(sol.price_unit ,0) 
			ELSE coalesce(sol.price_unit ,0)*coalesce(tc.sale_type,1)  
			END * coalesce(sml.quantity,0)))  -  
			(sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) )) as margen_ganancia,

					   
					   
			sml.product_id as product_id,
			pb.name as marca
			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking sp on sml.picking_id = sp.id

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id
				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id
				left join res_currency_rate tc on tc.name = (  so.date_order - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""
				inner join product_product pp on sml.product_id=pp.id
				inner join product_template pt on pt.id = pp.product_tmpl_id
				left join product_brand pb on pb.id = pt.product_brand_id
						LEFT JOIN ( SELECT t_pp.id,
							((     (max(t_pt.name->>'es_PE'::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
						FROM product_product t_pp
							JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
							LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
							LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
							LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
						GROUP BY t_pp.id) pname ON pname.id = pp.id
					where 
so.id is not null and
sp.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
						group by sml.product_id, sml.product_uom_id, pname.new_name, pp.default_code, pb.name
							order by margen_ganancia desc;
							""")
			cnslta = self.env.cr.dictfetchall()
			contador = 0
			output = io.BytesIO()
			workbook = Workbook(output, {'constant_memory': False})
			worksheet = workbook.add_worksheet("Reporte ABC")
			worksheet.set_column('A:A', 27)
			worksheet.set_column('B:B', 59)
			worksheet.set_column('C:C', 18.5)
			worksheet.set_column('D:D', 17.5)
			worksheet.set_column('E:E', 19)
			worksheet.set_column('F:F', 18.5)
			worksheet.set_column('G:G', 17.5)
			worksheet.set_column('H:H', 18.5)
			worksheet.set_column('I:I', 18.5)
			worksheet.set_column('J:J', 17.5)
			worksheet.set_column('K:K', 17.5)
			worksheet.set_column('L:L', 17.5)

			cell_titulo_bottom = workbook.add_format({'bold': True})
			cell_titulo_bottom.set_align('center')
			cell_titulo_bottom.set_font_name('Calibri')
			cell_titulo_bottom.set_font_size(26)
			cell_titulo_bottom.set_font_color('#2D45F3')


			cell_subtitle = workbook.add_format({'bold': True})
			cell_subtitle.set_align('center')
			cell_subtitle.set_bottom(1)
			cell_subtitle.set_top(1)
			cell_subtitle.set_left(1)
			cell_subtitle.set_right(1)
			cell_subtitle.set_font_name('Calibri')
			cell_subtitle.set_font_size(14)
			cell_subtitle.set_bg_color('#F3F5F5')


			cell_subtitle_sub = workbook.add_format({'bold': True})
			cell_subtitle_sub.set_align('left')
			cell_subtitle_sub.set_font_name('Calibri')
			cell_subtitle_sub.set_font_size(14)


			cell_texto_bottom_nta = workbook.add_format({'bold': False})
			cell_texto_bottom_nta.set_align('left')
			cell_texto_bottom_nta.set_bottom(1)
			cell_texto_bottom_nta.set_top(1)
			cell_texto_bottom_nta.set_left(1)
			cell_texto_bottom_nta.set_right(1)
			cell_texto_bottom_nta.set_font_name('Calibri')
			cell_texto_bottom_nta.set_font_size(12)
			

			cell_texto_numerotres = workbook.add_format({'bold': False})
			cell_texto_numerotres.set_align('right')
			cell_texto_numerotres.set_bottom(1)
			cell_texto_numerotres.set_top(1)
			cell_texto_numerotres.set_left(1)
			cell_texto_numerotres.set_right(1)
			cell_texto_numerotres.set_font_name('Calibri')
			cell_texto_numerotres.set_font_size(12)
			cell_texto_numerotres.set_num_format('0.000')

			cell_texto_numerodos = workbook.add_format({'bold': False})
			cell_texto_numerodos.set_align('right')
			cell_texto_numerodos.set_bottom(1)
			cell_texto_numerodos.set_top(1)
			cell_texto_numerodos.set_left(1)
			cell_texto_numerodos.set_right(1)
			cell_texto_numerodos.set_font_name('Calibri')
			cell_texto_numerodos.set_font_size(12)
			cell_texto_numerodos.set_num_format('0.00')

			worksheet.merge_range('A2:H4', str(self.company_id.name), cell_titulo_bottom)
			worksheet.write('A6', "Modalidad:", cell_subtitle_sub)
			worksheet.write('B6', "Rotación/Entregados" if self.import_product_type=='rotation'else "Ganancia/Precio", cell_subtitle_sub)
			worksheet.write('A7', "Fecha Inicio:", cell_subtitle_sub)
			worksheet.write('B7', str(self.fecha_in), cell_subtitle_sub)
			worksheet.write('A8', "Fecha Fin:", cell_subtitle_sub)
			worksheet.write('B8', str(self.fecha_fin), cell_subtitle_sub)


			worksheet.write('A10', "Codigo Producto", cell_subtitle)
			worksheet.write('B10', "Producto", cell_subtitle)
			worksheet.write('C10', "Marca", cell_subtitle)
			worksheet.write('D10', "Entregado", cell_subtitle)
			worksheet.write('E10', "UDM Entregado", cell_subtitle)
			worksheet.write('F10', "Costo Total", cell_subtitle)
			worksheet.write('G10', "Precio Total", cell_subtitle)
			worksheet.write('H10', "Margen", cell_subtitle)
			worksheet.write('I10', "% Acumulado", cell_subtitle)
			worksheet.write('J10', "Grupo", cell_subtitle)
			worksheet.write('K10', "Saldo Cantidad", cell_subtitle)
			worksheet.write('L10', "UDM", cell_subtitle)
			worksheet.write('M10', "Saldo Soles", cell_subtitle)
			
			
			margenes_totales = 0
			self.env.cr.execute("""select 
			(sum(   CASE 
					   	WHEN rc.name='PEN' 
							then coalesce(sol.price_unit ,0) 
						ELSE coalesce(sol.price_unit ,0) * 
						coalesce(tc.sale_type,1)  END * coalesce(sml.quantity,0)))  -  
						(sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) )) as margen_ganancia

			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking spc on sml.picking_id = spc.id

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id					   

				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id

				left join res_currency_rate tc on tc.name = ( so.date_order - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""

				inner join product_product pp on sml.product_id=pp.id
					where 
sol.id is not null and
spc.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
					;
							""")

#REVISAR
			prueba_consulta = self.env.cr.dictfetchall()
			margenes_totales=float(prueba_consulta[0]["margen_ganancia"])
#			for x in cnslta:
#				margenes_totales+=x["margen_ganancia"]
			#total_prc_abc = len(cnslta)
			grupo_a = 80
			grupo_b = 90
			linea = 10
			acumulado_porcetaje = 0
			for x in cnslta:
				
				udm_entregado = self.env["uom.uom"].sudo().browse(x["unidad_medida_entregado"])
				producto_obj = self.env['product.product'].browse(x['product_id'])
				linea += 1
				contador += 1
				acumulado_porcetaje +=  (((x["margen_ganancia"] if x["margen_ganancia"] else 0)*100)/margenes_totales) if margenes_totales!=0 else 100
				if acumulado_porcetaje <= grupo_a:
					grupo="Grupo A"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje <= grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo B"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje > grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo C"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				if producto_obj.id in dicc_guardado:
					dicc_guardado.pop(producto_obj.id)
			for resto in dicc_guardado:
				linea += 1
				grupo="Grupo D"
				worksheet.write('A'+str(linea), dicc_guardado[resto]["default_code"] if "default_code" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('B'+str(linea), dicc_guardado[resto]["producto"] if "producto" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('C'+str(linea), dicc_guardado[resto]["marca"] if "marca" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('D'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('E'+str(linea), "",cell_texto_bottom_nta)
				worksheet.write('F'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('G'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('H'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('I'+str(linea), 0,cell_texto_numerodos)
				worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
				worksheet.write('K'+str(linea), dicc_guardado[resto]["saldo_cantidad"] if "saldo_cantidad" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				worksheet.write('L'+str(linea), dicc_guardado[resto]["udm"] if "udm" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('M'+str(linea), dicc_guardado[resto]["saldo_soles"] if "saldo_soles" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				
				producto_obj = self.env['product.product'].browse(resto)
			linea +=1
			worksheet.write('H'+str(linea), margenes_totales,cell_texto_numerotres)
			workbook.close()
			output.seek(0)

			output_datas = base64.b64encode(output.getvalue())
			output.close()

			return self.env['popup.it'].get_file('Reporte ABC Ganancia-Margen.xlsx',output_datas)



			attach_id = self.env['ir.attachment'].create({
					'name': "Reporte ABC Ganancia-Margen.xlsx",
					'type': 'binary',
					'datas': base64.b64encode(output.read()),
					'eliminar_automatico': True
				})
			output.close()


			return {
				'type': 'ir.actions.client',
				'tag': 'notification_llikha',
				'params': {
					'title':'Reporte ABC',
					'type': 'success',
					'sticky': True,
					'message': 'Se Proceso Exitosamente',
					'next': {'type': 'ir.actions.act_window_close'},
					'buttons':[{
						'label':'Descargar Kardex Valorado',
						'model':'ir.attachment',
						'method':'get_download_ls',
						'id':attach_id.id,
						}
					],
				}
			}

























































		if self.import_product_type=="precio":
			self.env.cr.execute("""select 
pp.default_code as default_code, 
pname.new_name as producto,
sml.product_uom_id as unidad_medida_entregado,
sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) ) as costo_total,
sum(coalesce(sml.quantity,0)) as entregas_total,

sum(   CASE 
			WHEN rc.name='PEN' 
				then coalesce(sol.price_unit ,0) 
			ELSE coalesce(sol.price_unit ,0)*coalesce(tc.sale_type,1)  
			END * coalesce(sml.quantity,0)) as facturado_precio_total,

(sum(   CASE 
			WHEN rc.name='PEN' 
				then coalesce(sol.price_unit ,0) 
			ELSE coalesce(sol.price_unit ,0)*coalesce(tc.sale_type,1)  
			END * coalesce(sml.quantity,0)))  -  
			(sum(coalesce(sm.price_unit_it,0) * coalesce(sml.quantity,0) )) as margen_ganancia,

					   
					   
			sml.product_id as product_id,
			pb.name as marca
			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking sp on sml.picking_id = sp.id

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id
				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id
				left join res_currency_rate tc on tc.name = ( so.date_order - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""
				inner join product_product pp on sml.product_id=pp.id
				inner join product_template pt on pt.id = pp.product_tmpl_id
				left join product_brand pb on pb.id = pt.product_brand_id
						LEFT JOIN ( SELECT t_pp.id,
							((     (max(t_pt.name->>'es_PE'::text))::character varying::text || ' '::text) || replace(array_agg(pav.name)::character varying::text, '{NULL}'::text, ''::text))::character varying AS new_name
						FROM product_product t_pp
							JOIN product_template t_pt ON t_pp.product_tmpl_id = t_pt.id
							LEFT JOIN product_variant_combination pvc ON pvc.product_product_id = t_pp.id
							LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
							LEFT JOIN product_attribute_value pav ON pav.id = ptav.product_attribute_value_id
						GROUP BY t_pp.id) pname ON pname.id = pp.id
					where 
so.id is not null  and
sp.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
						group by sml.product_id, sml.product_uom_id, pname.new_name, pp.default_code, pb.name
							order by facturado_precio_total desc;
							""")
			cnslta = self.env.cr.dictfetchall()
			contador = 0
			output = io.BytesIO()
			workbook = Workbook(output, {'constant_memory': False})
			worksheet = workbook.add_worksheet("Reporte ABC")
			worksheet.set_column('A:A', 27)
			worksheet.set_column('B:B', 59)
			worksheet.set_column('C:C', 18.5)
			worksheet.set_column('D:D', 17.5)
			worksheet.set_column('E:E', 19)
			worksheet.set_column('F:F', 18.5)
			worksheet.set_column('G:G', 17.5)
			worksheet.set_column('H:H', 18.5)
			worksheet.set_column('I:I', 18.5)
			worksheet.set_column('J:J', 17.5)
			worksheet.set_column('K:K', 17.5)
			worksheet.set_column('L:L', 17.5)

			cell_titulo_bottom = workbook.add_format({'bold': True})
			cell_titulo_bottom.set_align('center')
			cell_titulo_bottom.set_font_name('Calibri')
			cell_titulo_bottom.set_font_size(26)
			cell_titulo_bottom.set_font_color('#2D45F3')


			cell_subtitle = workbook.add_format({'bold': True})
			cell_subtitle.set_align('center')
			cell_subtitle.set_bottom(1)
			cell_subtitle.set_top(1)
			cell_subtitle.set_left(1)
			cell_subtitle.set_right(1)
			cell_subtitle.set_font_name('Calibri')
			cell_subtitle.set_font_size(14)
			cell_subtitle.set_bg_color('#F3F5F5')


			cell_subtitle_sub = workbook.add_format({'bold': True})
			cell_subtitle_sub.set_align('left')
			cell_subtitle_sub.set_font_name('Calibri')
			cell_subtitle_sub.set_font_size(14)


			cell_texto_bottom_nta = workbook.add_format({'bold': False})
			cell_texto_bottom_nta.set_align('left')
			cell_texto_bottom_nta.set_bottom(1)
			cell_texto_bottom_nta.set_top(1)
			cell_texto_bottom_nta.set_left(1)
			cell_texto_bottom_nta.set_right(1)
			cell_texto_bottom_nta.set_font_name('Calibri')
			cell_texto_bottom_nta.set_font_size(12)
			

			cell_texto_numerotres = workbook.add_format({'bold': False})
			cell_texto_numerotres.set_align('right')
			cell_texto_numerotres.set_bottom(1)
			cell_texto_numerotres.set_top(1)
			cell_texto_numerotres.set_left(1)
			cell_texto_numerotres.set_right(1)
			cell_texto_numerotres.set_font_name('Calibri')
			cell_texto_numerotres.set_font_size(12)
			cell_texto_numerotres.set_num_format('0.000')

			cell_texto_numerodos = workbook.add_format({'bold': False})
			cell_texto_numerodos.set_align('right')
			cell_texto_numerodos.set_bottom(1)
			cell_texto_numerodos.set_top(1)
			cell_texto_numerodos.set_left(1)
			cell_texto_numerodos.set_right(1)
			cell_texto_numerodos.set_font_name('Calibri')
			cell_texto_numerodos.set_font_size(12)
			cell_texto_numerodos.set_num_format('0.00')

			worksheet.merge_range('A2:H4', str(self.company_id.name), cell_titulo_bottom)
			worksheet.write('A6', "Modalidad:", cell_subtitle_sub)
			worksheet.write('B6', "Precio Venta", cell_subtitle_sub)
			worksheet.write('A7', "Fecha Inicio:", cell_subtitle_sub)
			worksheet.write('B7', str(self.fecha_in), cell_subtitle_sub)
			worksheet.write('A8', "Fecha Fin:", cell_subtitle_sub)
			worksheet.write('B8', str(self.fecha_fin), cell_subtitle_sub)


			worksheet.write('A10', "Codigo Producto", cell_subtitle)
			worksheet.write('B10', "Producto", cell_subtitle)
			worksheet.write('C10', "Marca", cell_subtitle)
			worksheet.write('D10', "Entregado", cell_subtitle)
			worksheet.write('E10', "UDM Entregado", cell_subtitle)
			worksheet.write('F10', "Costo Total", cell_subtitle)
			worksheet.write('G10', "Precio Total", cell_subtitle)
			worksheet.write('H10', "Margen", cell_subtitle)
			worksheet.write('I10', "% Acumulado", cell_subtitle)
			worksheet.write('J10', "Grupo", cell_subtitle)
			worksheet.write('K10', "Saldo Cantidad", cell_subtitle)
			worksheet.write('L10', "UDM", cell_subtitle)
			worksheet.write('M10', "Saldo Soles", cell_subtitle)
			
			
			margenes_totales = 0
			self.env.cr.execute("""select 

		sum(   CASE 
			WHEN rc.name='PEN' 
				then coalesce(sol.price_unit ,0) 
			ELSE 
				coalesce(sol.price_unit ,0)*coalesce(tc.sale_type,1)  
			END * coalesce(sml.quantity,0)) as facturado_precio_total					   

			from stock_move_line sml
				inner join stock_location sl on sml.location_dest_id = sl.id
				inner join stock_move sm on sml.move_id=sm.id
				inner join stock_picking spc on sml.picking_id = spc.id

				left join sale_order_line sol on sm.sale_line_id=sol.id
				left join sale_order so on so.id = sol.order_id
				inner join product_pricelist pay on pay.id = so.pricelist_id
				inner join res_currency rc on rc.id = pay.currency_id

				left join res_currency_rate tc on tc.name = ( so.date_order - interval '5 hours')::date and tc.currency_id = pay.currency_id and tc.company_id="""+str(self.company_id.id)+"""

				inner join product_product pp on sml.product_id=pp.id
					where 
sol.id is not null  and
spc.company_id ="""+ str(self.company_id.id)+""" and sml.state = 'done' and sl.usage = 'customer' and (sm.kardex_date - interval '5 hours')::date >='"""+str(self.fecha_in)+"""' and (sm.kardex_date - interval '5 hours')::date <='"""+str(self.fecha_fin)+"""'
					;
							""")

#REVISAR
			prueba_consulta = self.env.cr.dictfetchall()
			margenes_totales=float(prueba_consulta[0]["facturado_precio_total"])
#			for x in cnslta:
#				margenes_totales+=x["margen_ganancia"]
			#total_prc_abc = len(cnslta)
			grupo_a = 80
			grupo_b = 90
			linea = 10
			acumulado_porcetaje = 0
			for x in cnslta:
				
				udm_entregado = self.env["uom.uom"].sudo().browse(x["unidad_medida_entregado"])
				producto_obj = self.env['product.product'].browse(x['product_id'])
				linea += 1
				contador += 1
				acumulado_porcetaje +=  (((x["facturado_precio_total"] if x["facturado_precio_total"] else 0)*100)/margenes_totales) if margenes_totales!=0 else 100
				if acumulado_porcetaje <= grupo_a:
					grupo="Grupo A"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje <= grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo B"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				elif acumulado_porcetaje > grupo_b and acumulado_porcetaje > grupo_a:
					grupo="Grupo C"
					worksheet.write('A'+str(linea), x["default_code"],cell_texto_bottom_nta)
					worksheet.write('B'+str(linea), x["producto"],cell_texto_bottom_nta)
					worksheet.write('C'+str(linea), x["marca"] if x["marca"] else "",cell_texto_bottom_nta)
					worksheet.write('D'+str(linea), x["entregas_total"],cell_texto_numerotres)
					worksheet.write('E'+str(linea), udm_entregado.name,cell_texto_bottom_nta)
					worksheet.write('F'+str(linea), x["costo_total"],cell_texto_numerotres)
					worksheet.write('G'+str(linea), x["facturado_precio_total"],cell_texto_numerotres)
					worksheet.write('H'+str(linea), (x["margen_ganancia"]),cell_texto_numerotres)
					worksheet.write('I'+str(linea), acumulado_porcetaje,cell_texto_numerodos)
					worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
					worksheet.write('K'+str(linea), dicc_guardado[producto_obj.id]["saldo_cantidad"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					worksheet.write('L'+str(linea), dicc_guardado[producto_obj.id]["udm"] if producto_obj.id in dicc_guardado else "",cell_texto_bottom_nta)
					worksheet.write('M'+str(linea), dicc_guardado[producto_obj.id]["saldo_soles"] if producto_obj.id in dicc_guardado else 0,cell_texto_bottom_nta)
					
				if producto_obj.id in dicc_guardado:
					dicc_guardado.pop(producto_obj.id)
			for resto in dicc_guardado:
				linea += 1
				grupo="Grupo D"
				worksheet.write('A'+str(linea), dicc_guardado[resto]["default_code"] if "default_code" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('B'+str(linea), dicc_guardado[resto]["producto"] if "producto" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('C'+str(linea), dicc_guardado[resto]["marca"] if "marca" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('D'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('E'+str(linea), "",cell_texto_bottom_nta)
				worksheet.write('F'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('G'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('H'+str(linea), 0,cell_texto_numerotres)
				worksheet.write('I'+str(linea), 0,cell_texto_numerodos)
				worksheet.write('J'+str(linea), grupo,cell_texto_bottom_nta)
				worksheet.write('K'+str(linea), dicc_guardado[resto]["saldo_cantidad"] if "saldo_cantidad" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				worksheet.write('L'+str(linea), dicc_guardado[resto]["udm"] if "udm" in dicc_guardado[resto] else "",cell_texto_bottom_nta)
				worksheet.write('M'+str(linea), dicc_guardado[resto]["saldo_soles"] if "saldo_soles" in dicc_guardado[resto] else 0,cell_texto_bottom_nta)
				
				producto_obj = self.env['product.product'].browse(resto)
			linea +=1
			worksheet.write('H'+str(linea), margenes_totales,cell_texto_numerotres)
			workbook.close()
			output.seek(0)
			output_datas = base64.b64encode(output.getvalue())
			output.close()

			return self.env['popup.it'].get_file('Reporte ABC Precio Venta.xlsx',output_datas)


			attach_id = self.env['ir.attachment'].create({
					'name': "Reporte ABC Precio Venta.xlsx",
					'type': 'binary',
					'datas': base64.encodestring(output.read()),
					'eliminar_automatico': True
				})
			output.close()


			return {
				'type': 'ir.actions.client',
				'tag': 'notification_llikha',
				'params': {
					'title':'Reporte ABC',
					'type': 'success',
					'sticky': True,
					'message': 'Se Proceso Exitosamente',
					'next': {'type': 'ir.actions.act_window_close'},
					'buttons':[{
						'label':'Descargar',
						'model':'ir.attachment',
						'method':'get_download_ls',
						'id':attach_id.id,
						}
					],
				}
			}
