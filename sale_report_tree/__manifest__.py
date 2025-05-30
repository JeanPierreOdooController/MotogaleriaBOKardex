# -*- coding: utf-8 -*-
{
    'name' : 'REPORTE TREE EN LISTA VENTAS',
    'version': '1.0',
    'author': 'ITGRUPO',
    'website': '',
    'category': 'Sale',
    'description':
        """
        Muestra en el REPORTE DEL MODULO DE VENTA, una nueva vista en forma listado.
        """,
    'depends' : ['sale','sale_stock'],
    #,'fxo_sale_order_approve'
    'data': [
        'views/sale_report.xml',        
    ],
    'auto_install': False,
    'installable': True
}