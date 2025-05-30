# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleAnalysisBook(models.Model):
    _name = 'sale.analysis.book'
    _auto = False
    vendedor = fields.Char(string='Vendedor')
    tipo = fields.Char(string='Tipo')
    id_user = fields.Integer(string="ID User")
    invoice_user_id = fields.Many2one('res.users', string="Vendedor Factura")
    td_partner = fields.Char(string='Tipo Doc. Partner')
    doc_partner = fields.Char(string='Doc. Partner')
    partner = fields.Char(string='Partner')
    fecha = fields.Date(string='Fecha')
    td_sunat = fields.Char(string='Tipo Doc. Factura')
    nro_comprobante = fields.Char(string='Nro Comprobante')
    estado_doc = fields.Char(string='Estado')
    category_name = fields.Char(string='Categoria')
    default_code = fields.Char(string='Referencia Interna')
    brand = fields.Char(string='Marca')
    product_id = fields.Many2one('product.product', string='Producto')
    standard_price = fields.Float(string='Costo Unitario',digits=(12, 4))
    id_product = fields.Integer(string='ID Producto')
    quantity = fields.Float(string='Cantidad', digits=(12, 2))
    list_price = fields.Float(string='Precio de Lista', digits=(12, 2))
    price_unit = fields.Float(string='P. Unitario', digits=(12, 4))
    importe_imp = fields.Float(string='Importe IMP', digits=(12, 4))
    tc = fields.Float(string='TC', digits=(12, 4))
    price_total = fields.Float(string='Costo Total', digits=(64, 4))
    balance = fields.Float(string='Subtotal', digits=(64, 4))
    monto_dolares = fields.Float(string='Monto Dolares', digits=(64, 4))
    cuenta = fields.Char(string='Cuenta')
    moneda = fields.Char(string='Moneda')
    ref_doc = fields.Char(string='Ref Documento')
    nomenclatura = fields.Char(string='Nomenclatura')
    move_id = fields.Many2one('account.move')
    team_vendor = fields.Char(string='Equipo Vendedor')
    flag = fields.Boolean('flag')
    plazopago = fields.Char('Plazo de Pago')
    datedue = fields.Date('Fecha de Vencimiento')
    lote = fields.Char('Lote')
    cat1 = fields.Char('Categoria de Producto N1')
    cat2 = fields.Char('Categoria de Producto N2')
    cat3 = fields.Char('Categoria de Producto N3')
    cat4 = fields.Char('Categoria de Producto N4')
    cat5 = fields.Char('Categoria de Producto N5')
    cat6 = fields.Char('Categoria de Producto N6')
    cat7 = fields.Char('Categoria de Producto N7')
    team = fields.Char('Equipo')
    
    pu_soles = fields.Float(string='P. Unitario S/.', digits=(12, 4))
    cu_soles = fields.Float(string='Costo Unitario S/.', digits=(12, 4))
    pt_soles = fields.Float(string='P. Total S/.', digits=(12, 4))
    ct_soles = fields.Float(string='Costo Total S/.', digits=(12, 4))
    marg_soles = fields.Float(string='Utilidad S/.', digits=(12, 4))
    marg_dolar = fields.Float(string='Utilidad $.', digits=(12, 4))
    pu_dolar = fields.Float(string='P. Unitario $.', digits=(12, 4))
    cu_dolar = fields.Float(string='Costo Unitario $.', digits=(12, 4))
    pt_dolar = fields.Float(string='P. Total $.', digits=(12, 4))
    ct_dolar = fields.Float(string='Costo Total $.', digits=(12, 4))

    
    departamento_id = fields.Many2one('res.country.state',string="Departamento")
    provincia_id = fields.Many2one('res.country.state',string="Provincia")
    distrito_id = fields.Many2one('res.country.state',string="Distrito")

    
    
                


    @api.depends('tc')
    def _update_tc(self):
        for l in self:
            orden = self.env['account.move'].search(
                [('company_id', '=', l.move_id.company_id.id), ('id', '=', l.move_id.id)])
            if orden:
                if orden.currency_rate == 1.0:
                    fecha = self.env['res.currency.rate'].search([('name', '=', l.fecha),('company_id', '=', l.move_id.company_id.id)])
                    l.tc = fecha.sale_type
                else:
                    l.tc = orden.currency_rate
            else:
                l.tc = orden.currency_rate
        

    @api.depends('id_product')
    def _update_product_category(self):
        for l in self:
            order = self.env['product.product'].search([('id', '=', l.id_product)])
            if order:
                if order.categ_id:
                    # producto_obj = self.env['product.product'].browse(l['product_id'])
                    cat_name = []
                    cat_obj = order.categ_id
                    while (cat_obj.id):
                        cat_name.append(cat_obj.name)
                        cat_obj = cat_obj.parent_id
                    cat_name.reverse()
                    cat_recortado = cat_name
                    l.cat1= cat_recortado[0] if len(cat_recortado)> 0 else ''
                    l.cat2= cat_recortado[1] if len(cat_recortado)> 1 else ''
                    l.cat3= cat_recortado[2] if len(cat_recortado)> 2 else ''
                    l.cat4= cat_recortado[3] if len(cat_recortado)> 3 else ''
                    l.cat5= cat_recortado[4] if len(cat_recortado)> 4 else ''
                    l.cat6= cat_recortado[5] if len(cat_recortado)> 5 else ''
                    l.cat7= cat_recortado[6] if len(cat_recortado)> 6 else ''
                else:
                    l.cat1 = ''
                    l.cat2 = ''
                    l.cat3 = ''
                    l.cat4 = ''
                    l.cat5 = ''
                    l.cat6 = ''
                    l.cat7 = ''
            else:
                l.cat1 = ''
                l.cat2 = ''
                l.cat3 = ''
                l.cat4 = ''
                l.cat5 = ''
                l.cat6 = ''
                l.cat7 = ''
        print('FIN _update_product_category')
    
    @api.depends('plazopago')
    def _update_payment_term(self):
        for l in self:
            order = self.env['account.move'].search(
                [('company_id', '=', l.move_id.company_id.id), ('id', '=', l.move_id.id)])
            if order:
                if order.team_id:
                    '''
                    self.env.cr.execute("UPDATE sale_analysis_book SET plazopago = '{}'  WHERE  id = {}".format(
                        str(order.invoice_payment_term_id.name), l.id))
                    '''
                    l.plazopago = order.invoice_payment_term_id.name
                else:
                    l.plazopago = ''
            else:
                l.plazopago = ''

    def _update_price_total(self):
        for i in self:
            if i.quantity and i.standard_price:
                i.price_total = i.quantity * i.standard_price
            else:
                i.price_total = 0


    @api.depends('team_vendor')
    def _change_team(self):
        for l in self:
            # vendedor = self.env['res.users'].search(
            #     [('company_id', '=', l.move_id.company_id.id), ('id', '=', l.id_user)])
            # if vendedor:
            #     if vendedor.sale_team_id:
            #         l.team_vendor = vendedor.sale_team_id.name
            #     else:
            #         l.team_vendor = ''
            # else:
            #     l.team_vendor = ''
            equipos = self.env['crm.team'].search([])
            for equipo in equipos:
                for usuario in equipo.team_user_ids:
                    if usuario.user_id.id == l.id_user:
                        l.team_vendor = equipo.name
                    else:
                        l.team_vendor = l.team_vendor                        
            if not l.team_vendor:
                l.team_vendor = l.move_id.team_id.name
            
