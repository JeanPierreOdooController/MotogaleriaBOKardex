# -*- coding: utf-8 -*-
{
    'name': "Marca Producto",
    'category': 'BO',
    'summary': """Marca Producto""",
    'version': '2.3',
    'author': 'ITGRUPO-KARDEX-JP',
    'description': """
        Marca Producto""",
    'depends': ['sale','product','kardex_fields_it'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_views.xml'
    ],
    'installable': True,
    'application': True
}
