# -*- coding: utf-8 -*-

from tkinter import E
from xml.dom import ValidationErr
 

from odoo import models, fields, api
from datetime import *
from odoo.exceptions import UserError

class SaleAnalysisWizard(models.TransientModel):
    _name = 'sale.analysis.wizard'

    name = fields.Char()
    company_id = fields.Many2one('res.company',string=u'Compañia',required=True, default=lambda self: self.env.company,readonly=True)
    fiscal_year_id = fields.Many2one('account.fiscal.year',string='Ejercicio',required=True)
    period_start = fields.Many2one('account.period',string='Periodo Inicial',required=True)
    period_end = fields.Many2one('account.period',string='Periodo Final',required=True)
    verify_groups_menu = fields.Boolean('Verificar menu', compute="_compute_verify_groups_menu")

    def _compute_verify_groups_menu(self):
        desired_group_name = self.env['res.groups'].search([('name','=','Equipo: Mostrar Documentos')])
        desired_user_gr = self.env.user.id in desired_group_name.users.ids
        if not self.env.user.has_group('sales_team.group_sale_salesman_all_leads') and not self.env.user.has_group('sales_team.group_sale_salesman') and not desired_user_gr:
            self.verify_groups_menu =  False
        else:
            self.verify_groups_menu =  True


    def get_report(self):
        self.env.cr.execute("""
            drop view if exists sale_analysis_book;
            CREATE OR REPLACE view sale_analysis_book as ("""+self._get_sql()+""")""")
        '''
        for l in self.env['sale.analysis.book'].search([]):
            order = self.env['sale.order'].search([('company_id','=',l.move_id.company_id.id),('name','=',l.move_id.invoice_origin)])
            if order:
                if order.team_id:
                    #self.env.cr.execute("UPDATE sale_analysis_book SET team_vendor = '{}'  WHERE  id = {}".format(str(order.team_id.name),l.id))
                    l.team_vendor = order.team_id.name
        '''

        return {
            'name': 'Analisis de Ventas',
            'type': 'ir.actions.act_window',
            'domain': [('tipo','in',('out_invoice','out_refund'))],
            'res_model': 'sale.analysis.book',
            'view_mode': 'tree,pivot,graph',
            'view_type': 'form',
        }

    def _get_sql(self):
        sql_filter = ""
        sql_filter_teams = ""
        # if not self.env.user.has_group('sale_analysis_it.group_sale_analysis_it'):
        #     sql_filter = " and rup.name = '%s'" % (self.env.user.name)
        desired_group_name = self.env['res.groups'].search([('name','=','Equipo: Mostrar Documentos')])
        desired_user_gr = self.env.user.id in desired_group_name.users.ids
        if not self.env.user.has_group('sales_team.group_sale_salesman_all_leads') and not self.env.user.has_group('sales_team.group_sale_salesman') and not desired_user_gr:
            raise UserError('Usted no tiene acceso a este reporte.')
        
        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            sql_filter = ""
        else:
            if self.env.user.has_group('sales_team.group_sale_salesman'):
                sql_filter = " and rup.name = '%s'" % (self.env.user.name)
            if desired_user_gr:
                es_jefe = False
                list_teams = ""
                conta = 1
                for equipos in self.env['crm.team'].search([]):
                    if self.env.user.id == equipos.user_id.id:
                        es_jefe = True
                        for users in equipos.team_user_ids:
                            if conta != 1:
                                list_teams += ","
                            list_teams += "%s" % (users.id)
                            conta += 1
                if not es_jefe:
                    raise UserError('Lo sentimos. Usted pertenece al grupo "Equipo: Mostrar Documentos", pero no es un jefe de equipo.')
                list_teams += ",%s" %(self.env.user.id)
                sql_filter = ""
                sql_filter_teams = "where o.team in (%s)" % (list_teams)

        sql = """
                select * from (
                select  
                T.* from(
                select 
                aml.id,
                CASE WHEN so.id is null THEN rup.name ELSE soru_rp.name END as vendedor,
                ru.sale_team_id as team,
                ru.id as id_user,
                lit.name->>'es_PE' as td_partner,
                vst.doc_partner,
                vst.partner,
                vst.fecha::date as fecha,
                --eic.name as td_sunat,
                vst.td_sunat,
                vst.nro_comprobante,
                case 
                    when am.payment_state = 'paid' then 'Pagado' else 'No pagado'
                end as estado_doc,
                aml.product_id as id_product,
                CASE WHEN - vst.balance <0 then -aml.quantity else
                aml.quantity END as quantity,
                CASE
                    WHEN aml.quantity is not null and aml.quantity != 0
                        THEN
                            round( (aml.debit+aml.credit) / aml.quantity :: numeric(64,2),2)
                    ELSE 0
                END as price_unit ,

                rc.name as moneda,
                CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,0) END as tc,
                aml.amount_currency*-1 as monto_dolares,
                pt.list_price,
                amr.ref as ref_doc,
                aml.product_id as product_id,
                pc.name as category_name,
                '' as cat7,
                '' as cat6,
                                  
                '' as cat5,
                       
                ''
                  as cat4,
                ''
                  as cat3,
                  
                pc1.name as cat2,
                
                pc.name  as cat1,
                 
                 
                pp.default_code,
                (
                CASE WHEN - vst.balance <0 then -aml.quantity else
                aml.quantity END )*albaran.precio_unitario as price_total,
                pb.name->>'es_PE' as brand,
                - vst.balance as balance,
                vst.cuenta,
                aa.name->>'es_PE' as nomenclatura,
                vst.move_id,
                ct.name->>'es_PE' as  team_vendor,
                -1*aml.tax_amount_it as importe_imp,
                albaran.precio_unitario as standard_price,
                case when pt.tracking = 'none' then true else false end as flag,
                COALESCE(apt.name->>'es_PE','CONTADO') as plazopago,
                am.invoice_date_due as datedue,
                albaran.lot as lote ,
                ru.id as invoice_user_id,
                am.move_type as tipo,

                CASE
                    WHEN aml.quantity is not null and aml.quantity != 0
                        THEN
                            round( (aml.debit+aml.credit) / aml.quantity :: numeric(64,2),2)
                    ELSE 0
                END as pu_soles,
                coalesce(albaran.precio_unitario,0) as cu_soles,
                (aml.debit+aml.credit) as pt_soles,
                coalesce(albaran.precio_unitario,0)*aml.quantity as ct_soles,
                ( (aml.debit+aml.credit) - (coalesce(albaran.precio_unitario,0)*aml.quantity)) as marg_soles,
                (CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END) as tipocambio,

                CASE
                    WHEN aml.quantity is not null and aml.quantity != 0
                        THEN
                            (round( (aml.debit+aml.credit) / aml.quantity :: numeric(64,2),2)) / (CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END)
                    ELSE 0
                        END as pu_dolar,

                    coalesce(albaran.precio_unitario,0)/ (CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END) as cu_dolar,


                (aml.debit+aml.credit) / (CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END) as pt_dolar,
                (coalesce(albaran.precio_unitario,0)*aml.quantity) / (CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END) as ct_dolar,
                (( (aml.debit+aml.credit) - (coalesce(albaran.precio_unitario,0)*aml.quantity)))/((CASE WHEN am.currency_rate != 1 and am.currency_rate != 0 THEN am.currency_rate else COALESCE( (select sale_type from res_currency_rate where name = vst.fecha::date limit 1 ) ,1) END)) as marg_dolar,

                rpmove.state_id  as  departamento_id,
rpmove.province_id as   provincia_id,
rpmove.district_id as   distrito_id
    
                
                from get_diariog('"""+str(self.period_start.date_start)+"""','"""+str(self.period_end.date_end)+"""',"""+str(self.company_id.id)+""") vst
                left join account_move am on am.id = vst.move_id
                left join account_move_line aml on aml.id = vst.move_line_id
                left join sale_order_line_invoice_rel rel on aml.id = rel.invoice_line_id
                left join sale_order_line sol on sol.id = rel.order_line_id
                left join sale_order so on so.id = sol.order_id
                left join res_users soru on soru.id = so.user_id
                left join res_partner soru_rp on soru_rp.id = soru.partner_id
                left join ( 
                        select  xaml.id , xaml.product_id, coalesce(max(xsm.price_unit_it),max(x2sm.price_unit_it) ) as precio_unitario, 
                        CASE WHEN max(xspl.id) is not null then
                        replace(replace(replace(array_agg(xspl.name)::varchar,'{',''),'}',''),'NULL','')
                        else 
                        replace(replace(replace(array_agg(x2spl.name)::varchar,'{',''),'}',''),'NULL','')
                        end as lot  from 
                        account_move_line xaml 
                        inner join account_move xam on xam.id = xaml.move_id
                        left join stock_move xsm on xsm.invoice_id = xam.id and xsm.product_id = xaml.product_id
                        left join stock_move_line xsml on xsml.move_id = xsm.id
                        left join stock_lot xspl on xspl.id = xsml.lot_id
                        left join sale_order_line_invoice_rel xrel on xrel.invoice_line_id = xaml.id
                        left join sale_order_line xsol on xsol.id = xrel.order_line_id
                        left join stock_move x2sm on x2sm.sale_line_id = xsol.id
                        left join stock_move_line x2sml on x2sml.move_id = x2sm.id
                        left join stock_lot x2spl on x2spl.id = x2sml.lot_id
                        group by xaml.id, xaml.product_id
                 ) as albaran on albaran.id = aml.id and albaran.product_id = aml.product_id
               
                left join res_users ru on ru.id = am.invoice_user_id
                left join res_partner rup on rup.id = ru.partner_id
                left join product_product pp on pp.id = aml.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join product_category pc on pc.id = pt.categ_id
                left join product_category pc1 on pc1.id = pc.parent_id
                left join product_category pc2 on pc2.id = pc1.parent_id
                left join product_category pc3 on pc3.id = pc2.parent_id
                left join product_category pc4 on pc4.id = pc3.parent_id
                left join product_category pc5 on pc5.id = pc4.parent_id
                left join product_category pc6 on pc6.id = pc5.parent_id
                left join product_category pc7 on pc7.id = pc6.parent_id
                left join product_brand pb on pb.id = pt.product_brand_id
                left join account_account aa on aa.id = vst.account_id
                left join res_partner rpmove on rpmove.id = aml.partner_id
                left join res_users ru_rpmove on ru_rpmove.id = rpmove.user_id
                left join res_partner rup_ru_rpmove on rup_ru_rpmove.id = ru_rpmove.partner_id
                left join l10n_latam_identification_type lit on lit.id = rpmove.l10n_latam_identification_type_id
                left join res_currency rc on rc.id = am.currency_id
                left join account_move amr on amr.id = am.reversed_entry_id
                left join crm_team ct on ct.id = am.team_id
                left join account_payment_term apt on apt.id = am.invoice_payment_term_id
                where (vst.periodo::int between %s and %s) and (left(vst.cuenta,2)='70' or left(vst.cuenta,3)='122')
                
                %s
                )T)o %s
        """ % (self.period_start.code,
        self.period_end.code,
        sql_filter, sql_filter_teams)

        return sql
