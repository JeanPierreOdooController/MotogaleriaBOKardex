# -*- coding: utf-8 -*-
{
    'name' : 'REPORTE DE COMPRA VISTA TREE',
    'version': '1.0',
    'author': 'ITGRUPO',
    'category': 'Purchase',
    'description':
        """
        Muestra en el REPORTE DEL MODULO DE COMPRA, una nueva vista en forma listado.
        """,
    'depends' : [
        'purchase',
        'purchase_stock',
        # 'purchase_enterprise'
    ],
    'data': [
        'views/purchase_report.xml',        
    ],
    'auto_install': False,
    'installable': True
}